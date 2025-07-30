from __future__ import annotations

from collections.abc import Callable, Generator, Iterable
from enum import StrEnum
from typing import TYPE_CHECKING

import pydantic
import sqlalchemy as sa
from pydantic import ConfigDict
from sqlalchemy.sql.schema import SchemaItem

from mitm_tooling.definition import MITM, ConceptName, MITMDefinition, RelationName, TypeName, get_mitm_def
from mitm_tooling.definition.definition_tools import ColGroupMaps, map_col_groups
from mitm_tooling.utilities.backports.sqlchemy_sql_views import create_view
from mitm_tooling.utilities.sql_utils import qualify

from ...data_types import MITMDataType
from ..intermediate.header import Header
from .common import Queryable, SchemaName, TableName

if TYPE_CHECKING:
    pass

SQL_REPRESENTATION_DEFAULT_SCHEMA = 'main'


class HeaderMetaTableName(StrEnum):
    KeyValue = 'header_meta_key_value'
    HeaderMetaDefinition = 'header_meta_definition'
    Types = 'header_meta_types'
    TypeAttributes = 'header_meta_type_attributes'


class HeaderMetaTables(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    key_value: sa.Table
    types: sa.Table
    type_attributes: sa.Table


ColumnsDict = dict[RelationName, sa.Column]
ViewsDict = dict[TableName, sa.Table]
ConceptTablesDict = dict[ConceptName, sa.Table]
ConceptTypeTablesDict = dict[ConceptName, dict[TypeName, sa.Table]]

MitMConceptSchemaItemGenerator = Callable[
    [MITM, ConceptName, SchemaName, TableName, ColumnsDict, ColumnsDict | None], Generator[SchemaItem, None, None]
]
MitMConceptColumnGenerator = Callable[[MITM, ConceptName], Generator[tuple[str, sa.Column], None, None]]
MitMDBViewsGenerator = Callable[
    [MITM, ConceptTablesDict, ConceptTypeTablesDict], Generator[tuple[TableName, Queryable], None, None]
]

ARTIFICIAL_ROW_ID_PREFIX = 'row'


def _prefix_col_name(prefix: str, name: str) -> str:
    return f'{prefix}_{name}'


def _get_unique_id_col_name(prefix: str | None = None) -> str:
    return '__' + ((prefix + '_') if prefix else '') + 'id'


def _within_concept_id_col(mitm: MITM, concept: ConceptName) -> str:
    parent_concept = get_mitm_def(mitm).get_parent(concept)
    return _get_unique_id_col_name(parent_concept)


class SQLRepresentationSchema(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    sa_meta: sa.MetaData
    meta_tables: HeaderMetaTables | None = None
    concept_tables: ConceptTablesDict = pydantic.Field(default_factory=ConceptTablesDict)
    type_tables: ConceptTypeTablesDict = pydantic.Field(default_factory=ConceptTypeTablesDict)
    views: ViewsDict = pydantic.Field(default_factory=ViewsDict)

    def get_concept_table(self, concept: ConceptName) -> sa.Table | None:
        return self.concept_tables.get(concept)

    def get_type_table(self, concept: ConceptName, type_name: TypeName) -> sa.Table | None:
        return self.type_tables.get(concept, {}).get(type_name)

    @property
    def tables_list(self) -> list[sa.Table]:
        return list(self.sa_meta.tables.values()) + list(self.views.values())


def mk_concept_table_name(mitm: MITM, concept: ConceptName) -> TableName:
    return get_mitm_def(mitm).get_properties(concept).plural


def mk_type_table_name(mitm: MITM, concept: ConceptName, type_name: RelationName) -> TableName:
    return get_mitm_def(mitm).get_properties(concept).key + '_' + type_name.lower()


def mk_link_table_name(mitm: MITM, concept: ConceptName, type_name: RelationName, fk_name: RelationName) -> TableName:
    return mk_type_table_name(mitm, concept, type_name) + '_' + fk_name.lower()


def has_type_tables(mitm_def: MITMDefinition, concept: ConceptName) -> bool:
    return mitm_def.get_properties(concept).permit_attributes


def has_natural_pk(mitm_def: MITMDefinition, concept: ConceptName) -> bool:
    return len(mitm_def.get_identity(concept)) > 0


def pick_table_pk(mitm: MITM, concept: ConceptName, created_columns: ColumnsDict) -> ColumnsDict | None:
    mitm_def = get_mitm_def(mitm)
    concept_properties, concept_relations = mitm_def.get(concept)

    prepended_cols = None
    if not has_natural_pk(mitm_def, concept):

        def prepended_cols():
            return [_within_concept_id_col(mitm, concept)]

    names, mapped_names = map_col_groups(
        mitm_def,
        concept,
        {
            'kind': lambda: 'kind',
            'type': lambda: concept_properties.typing_concept,
            'identity': lambda: list(concept_relations.identity),
        },
        prepended_cols=prepended_cols,
    )

    return {n: created_columns[n] for n in names}


def _gen_unique_constraint(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    yield sa.UniqueConstraint(*pk_columns.values())


def _gen_pk_constraint(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    yield sa.PrimaryKeyConstraint(*pk_columns.values())


def _gen_index(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    yield sa.Index(f'{table_name}.index', *pk_columns.values(), unique=True)


def _gen_foreign_key_constraints(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    mitm_def = get_mitm_def(mitm)
    _, concept_relations = mitm_def.get(concept)

    # self_fk
    if pk_columns:
        parent_concept = mitm_def.get_parent(concept)
        parent_table = mk_concept_table_name(mitm, parent_concept)
        cols, refcols = zip(
            *((c, qualify(schema=schema_name, table=parent_table, column=s)) for s, c in pk_columns.items()),
            strict=False,
        )
        yield sa.ForeignKeyConstraint(name='parent', columns=cols, refcolumns=refcols)

    for fk_name, fk_info in concept_relations.foreign.items():
        cols, refcols = zip(*fk_info.fk_relations.items(), strict=False)
        fkc = sa.ForeignKeyConstraint(
            name=fk_name,
            columns=[created_columns[c] for c in cols],
            refcolumns=[
                qualify(schema=schema_name, table=mk_concept_table_name(mitm, fk_info.target_concept), column=c)
                for c in refcols
            ],
        )
        yield fkc


_schema_item_generators: tuple[MitMConceptSchemaItemGenerator, ...] = (
    _gen_unique_constraint,
    _gen_pk_constraint,
    _gen_index,
    _gen_foreign_key_constraints,
)


def _gen_within_concept_id_col(mitm: MITM, concept: ConceptName) -> Generator[tuple[str, sa.Column], None, None]:
    n = _within_concept_id_col(mitm, concept)
    yield n, sa.Column(n, sa.Integer, nullable=False, unique=True, index=True)


_column_generators: tuple[MitMConceptColumnGenerator, ...] = (_gen_within_concept_id_col,)


def mk_table(
    meta: sa.MetaData,
    mitm: MITM,
    concept: ConceptName,
    table_name: TableName,
    col_group_maps: ColGroupMaps[sa.Column],
    additional_column_generators: Iterable[MitMConceptColumnGenerator] | None = (_gen_within_concept_id_col,),
    schema_item_generators: Iterable[MitMConceptSchemaItemGenerator] | None = (
        _gen_unique_constraint,
        _gen_pk_constraint,
        _gen_index,
    ),
    override_schema: SchemaName | None = None,
) -> tuple[sa.Table, ColumnsDict, ColumnsDict]:
    mitm_def = get_mitm_def(mitm)
    schema = override_schema if override_schema else SQL_REPRESENTATION_DEFAULT_SCHEMA

    prepended_cols = None
    if additional_column_generators is not None:

        def prepended_cols():
            return [c for generator in additional_column_generators for c in generator(mitm, concept)]

    columns, created_columns = map_col_groups(
        mitm_def, concept, col_group_maps, prepended_cols=prepended_cols, ensure_unique=True
    )

    pk_cols = pick_table_pk(mitm, concept, created_columns)

    schema_items: list[sa.sql.schema.SchemaItem] = []
    if schema_item_generators is not None:
        for generator in schema_item_generators:
            schema_items.extend(generator(mitm, concept, schema, table_name, created_columns, pk_cols))

    return sa.Table(table_name, meta, *columns, *schema_items, schema=schema), created_columns, pk_cols


def mk_header_tables(meta: sa.MetaData, override_schema: SchemaName | None = None) -> HeaderMetaTables:
    schema = override_schema if override_schema else SQL_REPRESENTATION_DEFAULT_SCHEMA

    header_meta_types = sa.Table(
        HeaderMetaTableName.Types,
        meta,
        sa.Column('kind', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('type', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('concept', MITMDataType.Text.sa_sql_type),
        schema=schema,
    )
    header_meta_type_attributes = sa.Table(
        HeaderMetaTableName.TypeAttributes,
        meta,
        sa.Column('kind', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('type', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('attribute_order', MITMDataType.Integer.sa_sql_type, primary_key=True),
        sa.Column('attribute_name', MITMDataType.Text.sa_sql_type),
        sa.Column('attribute_dtype', MITMDataType.Text.sa_sql_type),
        sa.ForeignKeyConstraint(
            name='header_meta_type',
            columns=['kind', 'type'],
            refcolumns=[header_meta_types.c.kind, header_meta_types.c.type],
        ),
        schema=schema,
    )

    header_meta_key_value = sa.Table(
        HeaderMetaTableName.KeyValue,
        meta,
        sa.Column('key', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('value', MITMDataType.Json.sa_sql_type),
        schema=schema,
    )

    return HeaderMetaTables(
        key_value=header_meta_key_value, types=header_meta_types, type_attributes=header_meta_type_attributes
    )


def _gen_denormalized_views(
    mitm: MITM, concept_tables: ConceptTablesDict, type_tables: ConceptTypeTablesDict
) -> Generator[tuple[TableName, Queryable], None, None]:
    mitm_def = get_mitm_def(mitm)

    for main_concept in mitm_def.main_concepts:
        for concept in mitm_def.get_leafs(main_concept):
            view_name = mk_concept_table_name(mitm, concept) + '_denormalized_view'
            q = None
            if has_type_tables(mitm_def, concept):
                selections = []

                for leaf_concept in mitm_def.get_leafs(concept):
                    if concept_type_tables := type_tables.get(leaf_concept):
                        col_sets = [{(c.name, str(c.type)) for c in t.columns} for t in concept_type_tables.values()]
                        set.intersection(*col_sets)
                        all_cols = set.union(*col_sets)

                        for _type_name, type_t in concept_type_tables.items():
                            selection = []
                            for col_name, col_type in all_cols:
                                if (c := type_t.columns.get(col_name)) is not None and str(c.type) == col_type:
                                    selection.append(c)
                                else:
                                    selection.append(sa.null().label(col_name))

                            # selection = (c if (c.name, str(c.type)) in shared_cols else sa.label(_prefix_col_name(type_name, c.name), c)
                            #             for c in type_t.columns)
                            selections.append(sa.select(*selection))

                if selections:
                    q = sa.union_all(*selections).subquery()
            else:
                if (concept_t := concept_tables.get(concept)) is not None:
                    # base_cols = {(c.name, str(c.type)) for c in concept_t.columns}
                    q = sa.select(concept_t)

            if q is not None:
                yield view_name, q

    for parent_concept, subs in mitm_def.sub_concept_map.items():
        if (concept_t := concept_tables.get(parent_concept)) is not None:
            for sub in subs:
                view_name = mk_concept_table_name(mitm, sub) + '_view'
                k = mitm_def.get_properties(sub).key
                q = sa.select(concept_t).where(concept_t.columns['kind'] == k)
                yield view_name, q


_view_generators: tuple[MitMDBViewsGenerator, ...] = (_gen_denormalized_views,)


# noinspection DuplicatedCode
def mk_sql_rep_schema(
    header: Header,
    view_generators: Iterable[MitMDBViewsGenerator] | None = (_gen_denormalized_views,),
    override_schema: SchemaName | None = None,
    skip_fk_constraints: bool = False,
    include_meta_tables: bool = True,
) -> SQLRepresentationSchema:
    schema_name = override_schema if override_schema else SQL_REPRESENTATION_DEFAULT_SCHEMA
    mitm_def = get_mitm_def(header.mitm)
    meta = sa.MetaData(schema=schema_name)

    concept_tables: ConceptTablesDict = {}
    type_tables: ConceptTypeTablesDict = {}
    views: dict[str, sa.Table] = {}

    base_schema_item_generators = (
        _gen_unique_constraint,
        _gen_pk_constraint,
        _gen_index,
    )
    for concept in mitm_def.main_concepts:
        concept_properties, concept_relations = mitm_def.get(concept)

        table_name = mk_concept_table_name(header.mitm, concept)

        def typ(concept_properties=concept_properties):
            return (
                concept_properties.typing_concept,
                sa.Column(concept_properties.typing_concept, MITMDataType.Text.sa_sql_type, nullable=False),
            )

        def identity(concept=concept):
            return [
                (name, sa.Column(name, dt.sa_sql_type, nullable=False))
                for name, dt in mitm_def.resolve_identity_type(concept).items()
            ]

        def inline(concept=concept):
            return [
                (name, sa.Column(name, dt.sa_sql_type)) for name, dt in mitm_def.resolve_inlined_types(concept).items()
            ]

        def foreign(concept=concept):
            return [
                (name, sa.Column(name, dt.sa_sql_type))
                for _, resolved_fk in mitm_def.resolve_foreign_types(concept).items()
                for name, dt in resolved_fk.items()
            ]

        t, t_columns, t_ref_columns = mk_table(
            meta,
            header.mitm,
            concept,
            table_name,
            col_group_maps={
                'kind': lambda: ('kind', sa.Column('kind', MITMDataType.Text.sa_sql_type, nullable=False)),
                'type': typ,
                'identity': identity,
                'inline': inline,
                'foreign': foreign,
            },
            additional_column_generators=(_gen_within_concept_id_col,),
            schema_item_generators=base_schema_item_generators,
            override_schema=schema_name,
        )
        concept_tables[concept] = t

    type_table_schema_item_generators = (
        base_schema_item_generators + (_gen_foreign_key_constraints,)
        if not skip_fk_constraints
        else base_schema_item_generators
    )
    for he in header.header_entries:
        he_concept = he.concept
        if has_type_tables(mitm_def, he_concept):
            concept_properties, concept_relations = mitm_def.get(he_concept)

            table_name = mk_type_table_name(header.mitm, he_concept, he.type_name)

            def typ(concept_properties=concept_properties):
                return (
                    concept_properties.typing_concept,
                    sa.Column(concept_properties.typing_concept, MITMDataType.Text.sa_sql_type, nullable=False),
                )

            def identity(he_concept=he_concept):
                return [
                    (name, sa.Column(name, dt.sa_sql_type, nullable=False))
                    for name, dt in mitm_def.resolve_identity_type(he_concept).items()
                ]

            def inline(he_concept=he_concept):
                return [
                    (name, sa.Column(name, dt.sa_sql_type))
                    for name, dt in mitm_def.resolve_inlined_types(he_concept).items()
                ]

            def foreign(he_concept=he_concept):
                return [
                    (name, sa.Column(name, dt.sa_sql_type))
                    for _, resolved_fk in mitm_def.resolve_foreign_types(he_concept).items()
                    for name, dt in resolved_fk.items()
                ]

            def attributes(he=he):
                return [(name, sa.Column(name, dt.sa_sql_type)) for name, dt in he.iter_attr_dtype_pairs()]

            t, t_columns, t_ref_columns = mk_table(
                meta,
                header.mitm,
                he_concept,
                table_name,
                {
                    'kind': lambda: ('kind', sa.Column('kind', MITMDataType.Text.sa_sql_type, nullable=False)),
                    'type': typ,
                    'identity': identity,
                    'inline': inline,
                    'foreign': foreign,
                    'attributes': attributes,
                },
                additional_column_generators=(_gen_within_concept_id_col,),
                schema_item_generators=type_table_schema_item_generators,
                override_schema=schema_name,
            )

            if he_concept not in type_tables:
                type_tables[he_concept] = {}
            type_tables[he_concept][he.type_name] = t

    if view_generators is not None:
        for generator in view_generators:
            for name, queryable in generator(header.mitm, concept_tables, type_tables):
                views[name] = create_view(name, queryable, meta, schema=schema_name)

    meta_tables = None
    if include_meta_tables:
        meta_tables = mk_header_tables(meta, override_schema=schema_name)

    return SQLRepresentationSchema(
        mitm=header.mitm,
        sa_meta=meta,
        meta_tables=meta_tables,
        concept_tables=concept_tables,
        type_tables=type_tables,
        views=views,
    )

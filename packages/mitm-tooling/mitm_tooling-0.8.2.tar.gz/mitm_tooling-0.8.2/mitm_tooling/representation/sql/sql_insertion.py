from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from typing import Any

import pandas as pd
import pydantic
import sqlalchemy as sa
from sqlalchemy import func

from mitm_tooling.definition import ConceptName, MITMDefinition, TypeName, get_mitm_def
from mitm_tooling.utilities.sql_utils import AnyDBBind, EngineOrConnection, use_nested_conn

from ..df import TypedMitMDataFrameStream
from ..intermediate.header import Header, HeaderEntry
from .sql_representation import SQLRepresentationSchema, _get_unique_id_col_name, has_type_tables


def insert_db_schema(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema) -> None:
    sql_rep_schema.sa_meta.create_all(bind=bind, checkfirst=True)


def drop_db_schema(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema) -> None:
    sql_rep_schema.sa_meta.drop_all(bind=bind, checkfirst=True)


def insert_header_data(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema, header: Header) -> None:
    if (meta_tables := sql_rep_schema.meta_tables) is not None:
        mitm_def_json = header.mitm_def.model_dump(mode='json', by_alias=True, exclude_unset=True, exclude_none=True)

        with use_nested_conn(bind) as conn:
            conn.execute(
                meta_tables.key_value.insert().values(
                    [{'key': 'mitm', 'value': header.mitm}, {'key': 'mitm_def', 'value': mitm_def_json}]
                )
            )

            if header.header_entries:
                conn.execute(
                    meta_tables.types.insert().values(
                        [{'kind': he.kind, 'type': he.type_name, 'concept': he.concept} for he in header.header_entries]
                    )
                )

                conn.execute(
                    meta_tables.type_attributes.insert().values(
                        [
                            {
                                'kind': he.kind,
                                'type': he.type_name,
                                'attribute_order': i,
                                'attribute_name': a,
                                'attribute_dtype': str(dt),
                            }
                            for he in header.header_entries
                            for i, (a, dt) in enumerate(he.iter_attr_dtype_pairs())
                        ]
                    )
                )
            # conn.commit()


def drop_header_data(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema) -> None:
    if (meta_tables := sql_rep_schema.meta_tables) is not None:
        with use_nested_conn(bind) as conn:
            meta_tables.key_value.drop(conn)
            meta_tables.type_attributes.drop(conn)
            meta_tables.types.drop(conn)
            # conn.commit()


def update_header_data(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema, header: Header) -> None:
    drop_header_data(bind, sql_rep_schema)
    insert_header_data(bind, sql_rep_schema, header)


def _df_to_records(
    df: pd.DataFrame, cols: Sequence[str], additional_cols: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    if additional_cols:
        df = df.assign(**additional_cols)
    return df[[c for c in cols if c in df.columns]].to_dict('records')


def _df_to_table_records(
    df: pd.DataFrame, table: sa.Table, additional_cols: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return _df_to_records(df, [c.name for c in table.columns], additional_cols=additional_cols)


def _insert_type_df(
    conn: sa.Connection,
    sql_rep_schema: SQLRepresentationSchema,
    mitm_def: MITMDefinition,
    concept: ConceptName,
    type_name: TypeName,
    type_df: pd.DataFrame,
    artificial_id_offset: int | None = None,
) -> tuple[int, int]:
    parent_concept = mitm_def.get_parent(concept)
    inserted_rows, no_instances = 0, 0
    if (t_concept := sql_rep_schema.get_concept_table(parent_concept)) is not None:
        # if not has_natural_pk(mitm, concept):
        # TODO not pretty..
        # ideally, I'd use the returned "inserted_pk"
        # values from the bulk insertion with an autoincrement id col
        # but apparently almost no DBABI drivers support this
        no_instances = len(type_df)
        concept_id_col_name = _get_unique_id_col_name(parent_concept)
        max_id = conn.execute(sa.select(func.max(t_concept.columns[concept_id_col_name]))).scalar() or 0
        start_id = max_id + (artificial_id_offset or 0) + 1
        artificial_ids = pd.RangeIndex(start=start_id, stop=start_id + no_instances, name=concept_id_col_name)
        # type_df[concept_id_col_name] = artificial_ids
        type_df = type_df.assign(**{concept_id_col_name: artificial_ids})
        conn.execute(t_concept.insert(), _df_to_table_records(type_df, t_concept))
        inserted_rows += no_instances

    if has_type_tables(mitm_def, concept):
        if (t_type := sql_rep_schema.get_type_table(concept, type_name)) is not None:
            # generated_ids = conn.execute(sa.select(t_concept.columns[concept_id_col_name])).scalars()
            conn.execute(t_type.insert(), _df_to_table_records(type_df, t_type))
            inserted_rows += no_instances
    return no_instances, inserted_rows


def _insert_type_dfs(
    conn: sa.Connection,
    sql_rep_schema: SQLRepresentationSchema,
    mitm_def: MITMDefinition,
    concept: ConceptName,
    typed_dfs: Iterable[tuple[TypeName, HeaderEntry, Iterable[pd.DataFrame]]],
) -> tuple[list[HeaderEntry], int, int]:
    total_inserted_instances, total_inserted_rows = 0, 0
    offsets = defaultdict(int)
    inserted_types = []
    for type_name, he, type_dfs in typed_dfs:
        inserted_types.append(he)
        for type_df in type_dfs:
            inserted_instances, inserted_rows = _insert_type_df(
                conn, sql_rep_schema, mitm_def, concept, type_name, type_df, artificial_id_offset=offsets[type_name]
            )
            offsets[type_name] += inserted_instances
            total_inserted_instances += inserted_instances
            total_inserted_rows += inserted_rows
    return inserted_types, total_inserted_instances, total_inserted_rows


class SQLRepInsertionResult(pydantic.BaseModel):
    inserted_types: list[HeaderEntry]
    inserted_instances: int
    inserted_rows: int


def insert_instances(
    bind: AnyDBBind, sql_rep_schema: SQLRepresentationSchema, instances: TypedMitMDataFrameStream
) -> SQLRepInsertionResult:
    total_inserted_instances, total_inserted_rows = 0, 0
    total_inserted_types = []
    mitm_def = get_mitm_def(sql_rep_schema.mitm)
    with use_nested_conn(bind) as conn:
        for concept, typed_dfs in instances:
            inserted_types, inserted_instances, inserted_rows = _insert_type_dfs(
                conn, sql_rep_schema, mitm_def, concept, typed_dfs
            )
            total_inserted_instances += inserted_instances
            total_inserted_rows += inserted_rows
            total_inserted_types.extend(inserted_types)
        # conn.commit()
    return SQLRepInsertionResult(
        inserted_instances=total_inserted_instances,
        inserted_rows=total_inserted_rows,
        inserted_types=total_inserted_types,
    )


def insert_data(
    bind: AnyDBBind,
    gen_sql_rep_schema: Callable[[], SQLRepresentationSchema],
    gen_instances: Callable[[], TypedMitMDataFrameStream],
    gen_override_header: Callable[[], Header] | None = None,
) -> SQLRepInsertionResult:
    sql_rep_schema = gen_sql_rep_schema()
    insert_db_schema(bind, sql_rep_schema)
    insertion_result = insert_instances(bind, sql_rep_schema, gen_instances())
    if gen_override_header:
        header = gen_override_header()
    else:
        header = Header(mitm=sql_rep_schema.mitm, header_entries=frozenset(insertion_result.inserted_types))
    insert_header_data(bind, sql_rep_schema, header)
    return insertion_result


def append_data(
    bind: AnyDBBind,
    gen_sql_rep_schema: Callable[[], SQLRepresentationSchema],
    gen_instances: Callable[[], TypedMitMDataFrameStream],
) -> SQLRepInsertionResult:
    sql_rep_schema = gen_sql_rep_schema()
    insertion_result = insert_instances(bind, sql_rep_schema, gen_instances())
    update_header_data(
        bind,
        sql_rep_schema,
        Header(mitm=sql_rep_schema.mitm, header_entries=frozenset(insertion_result.inserted_types)),
    )
    return insertion_result

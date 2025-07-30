import sqlalchemy as sa
from pydantic import AnyUrl

from mitm_tooling.extraction.sql.mapping import Exportable
from mitm_tooling.representation.df import TypedMitMDataFrameStream
from mitm_tooling.representation.intermediate import MITMData
from mitm_tooling.representation.sql import (
    SQLRepInsertionResult,
    SQLRepresentationSchema,
    insert_data,
    mk_sql_rep_schema,
)
from mitm_tooling.representation.sql.sql_insertion import append_data
from mitm_tooling.utilities.io_utils import FilePath
from mitm_tooling.utilities.sql_utils import AnyDBBind, EngineOrConnection, create_sa_engine


def insert_mitm_data(
    bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema, mitm_data: MITMData
) -> SQLRepInsertionResult:
    def instances() -> TypedMitMDataFrameStream:
        from mitm_tooling.transformation.df import mitm_data_into_mitm_dataframes

        return mitm_data_into_mitm_dataframes(mitm_data).typed_stream()

    return insert_data(bind, lambda: sql_rep_schema, instances, gen_override_header=lambda: mitm_data.header)


def insert_exportable(
    target: AnyDBBind,
    sql_rep_schema: SQLRepresentationSchema,
    source: AnyDBBind,
    exportable: Exportable,
    stream_data: bool = False,
) -> SQLRepInsertionResult:
    def instances() -> TypedMitMDataFrameStream:
        from mitm_tooling.transformation.df import exportable_to_typed_mitm_dataframes_stream

        return exportable_to_typed_mitm_dataframes_stream(source, exportable, stream_data=stream_data)

    return insert_data(target, lambda: sql_rep_schema, instances)


def append_exportable(
    target: AnyDBBind,
    sql_rep_schema: SQLRepresentationSchema,
    source: AnyDBBind,
    exportable: Exportable,
    stream_data: bool = False,
) -> SQLRepInsertionResult:
    def instances() -> TypedMitMDataFrameStream:
        from mitm_tooling.transformation.df import exportable_to_typed_mitm_dataframes_stream

        return exportable_to_typed_mitm_dataframes_stream(source, exportable, stream_data=stream_data)

    return append_data(target, lambda: sql_rep_schema, instances)


def mk_sqlite(
    mitm_data: MITMData, file_path: FilePath | None = ':memory:', autoclose: bool = True
) -> tuple[sa.Engine, SQLRepresentationSchema]:
    engine = create_sa_engine(AnyUrl(f'sqlite:///{str(file_path)}'), poolclass=sa.StaticPool)
    sql_rep_schema = mk_sql_rep_schema(mitm_data.header)
    insert_mitm_data(engine, sql_rep_schema, mitm_data)
    if autoclose:
        engine.dispose()
    return engine, sql_rep_schema

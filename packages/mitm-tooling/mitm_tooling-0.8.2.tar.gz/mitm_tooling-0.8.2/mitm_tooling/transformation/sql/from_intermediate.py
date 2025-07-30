from mitm_tooling.extraction.sql.data_models import DBMetaInfo
from mitm_tooling.representation.intermediate import Header, MITMData
from mitm_tooling.representation.sql import mk_sql_rep_schema


def header_into_db_meta(header: Header, override_schema: str | None = None) -> DBMetaInfo:
    from .from_sql import sql_rep_schema_into_db_meta

    sql_rep_schema = mk_sql_rep_schema(header, override_schema=override_schema)
    return sql_rep_schema_into_db_meta(sql_rep_schema)


def mitm_data_into_db_meta(mitm_data: MITMData, override_schema: str | None = None) -> DBMetaInfo:
    return header_into_db_meta(mitm_data.header, override_schema=override_schema)

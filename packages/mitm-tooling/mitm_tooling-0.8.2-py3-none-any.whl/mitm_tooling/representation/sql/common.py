from sqlalchemy import FromClause

TableName = str
SchemaName = str
ShortTableIdentifier = tuple[SchemaName, TableName]
QualifiedTableName = str
Queryable = FromClause

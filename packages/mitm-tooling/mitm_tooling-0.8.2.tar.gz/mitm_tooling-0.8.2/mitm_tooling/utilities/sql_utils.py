from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

import sqlalchemy as sa
from pydantic import AnyUrl
from sqlalchemy import Connection, Engine
from sqlalchemy.orm.session import Session

from .io_utils import FilePath

SQLiteFileOrEngine = FilePath | sa.Engine
EngineOrConnection = Engine | Connection
AnyDBBind = EngineOrConnection | Session


def qualify(*, table: str, schema: str | None = None, column: str | None = None):
    res = table
    if schema is not None:
        res = schema + '.' + res
    if column is not None:
        res += '.' + column
    return res


def unqualify(n: str) -> list[str]:
    return n.split('.')


def create_sa_engine(db_url: AnyUrl, test_engine: bool = False, **engine_kwargs) -> Engine:
    engine = sa.create_engine(str(db_url), **engine_kwargs)
    return engine


def any_url_into_sa_url(url: AnyUrl) -> sa.engine.URL:
    return sa.engine.make_url(str(url))


def sa_url_into_any_url(url: sa.engine.URL) -> AnyUrl:
    return AnyUrl(url.render_as_string(hide_password=False))


def dialect_cls_from_url(url: AnyUrl) -> type[sa.engine.Dialect]:
    return any_url_into_sa_url(url).get_dialect()


@contextmanager
def use_nested_conn(bind: AnyDBBind) -> Generator[Connection, None, None]:
    if isinstance(bind, Engine):
        with bind.connect() as conn:
            with conn.begin_nested():
                yield conn
    elif isinstance(bind, Connection):
        with bind.begin_nested():
            yield bind
    elif isinstance(bind, Session):
        with bind.begin_nested():
            yield bind.connection()
    else:
        raise TypeError(f'Expected Engine, Connection or Session, got {type(bind)}')


@contextmanager
def use_db_bind(bind: AnyDBBind) -> Generator[Connection, None, None]:
    if isinstance(bind, Session):
        yield bind.connection()
    elif isinstance(bind, Connection):
        yield bind
    elif isinstance(bind, Engine):
        yield bind.connect()
    else:
        raise TypeError(f'Expected Engine, Connection or Session, got {type(bind)}')

import contextlib
import json

from typing import Iterator

import ydb

from sqlalchemy.orm import (
    Session,
    sessionmaker,
)
from sqlalchemy.engine import (
    Engine,
    create_engine,
    Connection,
)

import settings

from logger import logger
from models import Table


class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: Engine | None = None
        self._sessionmaker: sessionmaker[Session] | None = None

    def init(self, db_url: str, **connect_args) -> None:
        if "postgresql" in db_url:
            connect_args.update({
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            })
        self._engine = create_engine(
            url=db_url,
            connect_args=connect_args,
        )
        self._sessionmaker = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )
        logger.info("DB initialized")

    def close(self) -> None:
        if self._engine is None:
            return
        self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        if self._sessionmaker is None:
            raise IOError("DatabaseSessionManager is not initialized")
        with self._sessionmaker() as session:
            try:
                yield session
            except Exception:
                session.rollback()
                raise

    @contextlib.contextmanager
    def connect(self) -> Iterator[Connection]:
        if self._engine is None:
            raise IOError("DatabaseSessionManager is not initialized")
        with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise


db_manager = DatabaseSessionManager()
db_manager.init(
    settings.YDB_URL,
    credentials=ydb.iam.ServiceAccountCredentials.from_content(json.dumps(settings.SA_KEY)),
    protocol="grpcs",
)


def create_tables() -> None:
    with db_manager.connect() as conn:
        Table.metadata.create_all(conn)

    logger.info("Tables was created")


@contextlib.contextmanager
def get_session() -> Iterator[Session]:
    with db_manager.session() as session:
        yield session

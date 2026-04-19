import contextlib

from typing import Any, Iterator

from sqlalchemy.orm import (
    Session,
    sessionmaker,
)
from sqlalchemy.engine import (
    create_engine,
    Connection,
)

from apps.core.models import Model

from logger import logger
import settings


class DBSessionManager:
    def __init__(self, url: str, **connect_args: Any) -> None:
        if "postgresql" in url:
            connect_args.update({
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            })

        self._engine = create_engine(
            url=url,
            connect_args=connect_args,
            echo=True,
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

    def create_tables(self) -> None:
        with self.connect() as conn:
            Model.metadata.create_all(conn)

        logger.info("Tables was created")


db_manager = DBSessionManager(**settings.DATABASE)

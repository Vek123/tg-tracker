import json

from typing import Any, Callable, Mapping

from aiogram.exceptions import DataNotDictLikeError
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType, State, KeyBuilder, DefaultKeyBuilder
from sqlalchemy import delete, select

from db import get_session, Session
from models import Fsm


class YDBStorage(BaseStorage):
    def __init__(
        self,
        key_builder: KeyBuilder | None = None,
        get_session: Callable[[], Session] = get_session,
    ):
        if key_builder is None:
            key_builder = DefaultKeyBuilder()

        self.key_builder = key_builder
        self.get_session = get_session

    def resolve_state(self, value: StateType) -> str | None:
        if value is None:
            return None

        if isinstance(value, State):
            return value.state

        return str(value)

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        """
        Set state for specified key

        :param key: storage key
        :param state: new state
        """
        key = self.key_builder.build(key, "state")
        value = self.resolve_state(state)
        query = select(Fsm).where(Fsm.key == key).with_for_update()
        with self.get_session() as session:
            fsm = session.execute(query).scalars().first()
            if not fsm:
                fsm = Fsm(key=key, value=value)
                session.add(fsm)
            else:
                fsm.value = value

            session.commit()

    async def get_state(self, key: StorageKey) -> str | None:
        """
        Get key state

        :param key: storage key
        :return: current state
        """
        key = self.key_builder.build(key, "state")
        query = select(Fsm.value).where(Fsm.key == key)
        with self.get_session() as session:
            state = session.execute(query).scalars().first()
            return state

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:  # noqa: F821
        """
        Write data (replace)

        :param key: storage key
        :param data: new data
        """
        if not isinstance(data, dict):
            msg = f"Data must be a dict or dict-like object, got {type(data).__name__}"
            raise DataNotDictLikeError(msg)

        key = self.key_builder.build(key, "data")
        value = json.dumps(data)
        with self.get_session() as session:
            if not data:
                query = delete(Fsm).where(Fsm.key == key)
                session.execute(query)
                session.commit()
                return

            query = select(Fsm).where(Fsm.key == key).with_for_update()
            fsm = session.execute(query).scalars().first()
            if not fsm:
                fsm = Fsm(key=key, value=value)
                session.add(fsm)
            else:
                fsm.value = value

            session.commit()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        """
        Get current data for key

        :param key: storage key
        :return: current data
        """
        key = self.key_builder.build(key, "data")
        query = select(Fsm).where(key == key)
        with self.get_session() as session:
            fsm = session.execute(query).scalars().first()
            if not fsm:
                return {}

            return json.loads(fsm.value)

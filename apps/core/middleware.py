from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from db.core import db_manager


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ):
        session = db_manager.session().__enter__()
        data["db_session"] = session
        response = await handler(event, data)
        session.__exit__(None, None, None)
        return response

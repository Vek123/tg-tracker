from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from db.core import db_manager


class Middleware(BaseMiddleware):
    observers: list[str]


class DBSessionMiddleware(Middleware):
    observers = [
        "message",
        "callback_query",
    ]
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ):
        session = db_manager.session().__enter__()
        data["db_session"] = session
        response = await handler(event, data)
        session.__exit__(None, None, None)
        return response

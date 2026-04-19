from typing import Any, Awaitable, Callable

from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from apps.account.models import User
from apps.core.middleware import Middleware


class GetUserMiddleware(Middleware):
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
        query = (
            select(User)
            .where(User.tg_id == event.from_user.id)
            .options(joinedload(User.mcp))
        )
        session = data["db_session"]
        user = session.execute(query).scalar_one_or_none()
        if user is None:
            user = User(tg_id=event.from_user.id)
            session.add(user)
            session.commit()

        data["user"] = user
        return await handler(event, data)

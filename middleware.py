from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from settings import create_iam_token
from vault import YCVaultService


class VaultMiddleware(BaseMiddleware):
    def __init__(self):
        self.service = YCVaultService(create_iam_token())

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ):
        data["vault"] = self.service
        return await handler(event, data)

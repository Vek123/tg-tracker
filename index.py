import asyncio
import json
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import settings

from apps.fsm import init_fsm_storage
from db.core import db_manager
from logger import logger
from routes import router
from utils.import_ import import_attr


async def handle_request(message: dict[str, Any]):
    logger.info(f"Handle incoming message: {message}")
    response = await dp.feed_webhook_update(bot, message)
    logger.info(f"Got response: {response}")


async def handler(event, context):
    await handle_request(json.loads(event["body"]))
    return {
        "statusCode": 200,
        "body": "",
    }


def register_middlewares(dp: Dispatcher, middlewares_paths: list[str]):
    for path in middlewares_paths:
        cls = import_attr(path)
        for observer in cls.observers:
            dp.observers[observer].middleware(cls())


db_manager.create_tables()
dp = Dispatcher(storage=init_fsm_storage())
bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))

dp.include_router(router)
register_middlewares(dp, settings.MIDDLEWARE)
# asyncio.run(dp.start_polling(bot))

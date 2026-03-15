import json
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import settings

from db import create_tables
from fsm import YDBStorage
from logger import logger
from middleware import VaultMiddleware
from routes import router

create_tables()
dp = Dispatcher(storage=YDBStorage())
bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
dp.include_router(router)
dp.message.middleware(VaultMiddleware())


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

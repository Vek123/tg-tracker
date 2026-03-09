from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

import settings

from fsm import YDBStorage
from logger import init_logger

init_logger()
dp = Dispatcher(storage=YDBStorage)
bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(ParseMode.MARKDOWN_V2))
webhook_request_handler = SimpleRequestHandler(
    dp,
    bot,
)


async def handle_request(event):
    await webhook_request_handler.handle(event)

async def handler(event, context):
    await handle_request(event)
    return {
        "statusCode": 200,
        "body": "",
    }

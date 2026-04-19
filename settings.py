import dataclasses
import json
import os

import dotenv
import ydb

from apps.auth.schemas import SAKey
from apps.auth.utils import create_iam_token, create_jwt_token

dotenv.load_dotenv(".env")

BOT_TOKEN = os.environ["BOT_TOKEN"]

ENV = os.environ.get("ENV", "prod")
SA_KEY = SAKey(**json.loads(os.environ["SA_KEY"]))
YC_FOLDER_ID = os.environ["YC_FOLDER_ID"]
JWT_TOKEN = create_jwt_token(SA_KEY)
IAM_TOKEN = create_iam_token(SA_KEY)
API_KEY = os.environ["API_KEY"]

AI_CHAT_BASE_URL = "https://ai.api.cloud.yandex.net/v1"

DATABASE = {
    "url": os.environ["YDB_URL"],
    "credentials": ydb.iam.ServiceAccountCredentials.from_content(json.dumps(dataclasses.asdict(SA_KEY))),
    "protocol": "grpcs",
}

FSM_STORAGE = {
    "path": "apps.fsm.ydb.YDBStorage",
}

MIDDLEWARE = (
    "apps.core.middleware.DBSessionMiddleware",
    "apps.account.middleware.GetUserMiddleware",
)

YC_AI_MODEL_URL = f"gpt://{YC_FOLDER_ID}/yandexgpt/rc"

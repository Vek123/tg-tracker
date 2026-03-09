import json
import os
from pathlib import Path

import time
import dotenv
import jwt

import yandexcloud

from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub

dotenv.load_dotenv(".env")

BOT_TOKEN = os.environ["BOT_TOKEN"]

ENV = os.environ.get("ENV", "prod")
YDB_URL = os.environ["YDB_URL"]
SA_KEY = json.loads(os.environ["SA_KEY"])


def create_jwt_token():
    now = int(time.time())
    payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': SA_KEY["service_account_id"],
            'iat': now,
            'exp': now + 3600
        }

    encoded_token = jwt.encode(
        payload,
        SA_KEY["private_key"],
        algorithm='PS256',
        headers={'kid': SA_KEY["id"]}
    )

    return encoded_token


def create_iam_token():
    jwt = create_jwt_token()
    sdk = yandexcloud.SDK(
        service_account_key={
            "id": SA_KEY["id"],
            "service_account_id": SA_KEY["service_account_id"],
            "private_key": SA_KEY["private_key"],
        },
    )
    iam_service = sdk.client(IamTokenServiceStub)
    iam_token = iam_service.Create(
        CreateIamTokenRequest(jwt=jwt)
    )
    return iam_token.iam_token

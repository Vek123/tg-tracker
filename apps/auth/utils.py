import time
import jwt

import yandexcloud

from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub

from apps.auth.schemas import SAKey


def create_jwt_token(sa_key: SAKey) -> str:
    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': sa_key.service_account_id,
        'iat': now,
        'exp': now + 3600
    }
    encoded_token = jwt.encode(
        payload,
        sa_key.private_key,
        algorithm='PS256',
        headers={'kid': sa_key.id},
    )
    return encoded_token


def create_iam_token(sa_key: SAKey):
    jwt = create_jwt_token(sa_key)
    sdk = yandexcloud.SDK(
        service_account_key={
            "id": sa_key.id,
            "service_account_id": sa_key.service_account_id,
            "private_key": sa_key.private_key,
        },
    )
    iam_service = sdk.client(IamTokenServiceStub)
    iam_token = iam_service.Create(
        CreateIamTokenRequest(jwt=jwt),
    )
    return iam_token.iam_token
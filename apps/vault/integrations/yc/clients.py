import time
from typing import Any

import requests


from .schemas import (
    Base,
    OperationResponse,
    Payload,
    SecretCreateIn,
    SecretCreateOut,
    SecretUpdateIn,
    SecretUpdateVersionIn,
    SecretUpdateVersionOut,
)



class HTTPClient:
    operation_base_url = "https://operation.api.cloud.yandex.net/operations"

    def __init__(self):
        self.session = requests.Session()

    def request[T](
        self,
        url: str,
        response_type: T | None = None,
        method: str = "get",
        data: Base | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        is_operation: bool = True,
    ) -> T:
        if response_type is None:
            response_type = dict

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data and data.model_dump(),
            headers=headers,
        )
        response.raise_for_status()
        if is_operation:
            response = OperationResponse.model_validate(response.json())
            response = self.wait_operation(response, headers)
            return response_type(**response.response)

        return response_type(**response.json())

    def wait_operation(self, data: OperationResponse, headers: dict[str, Any]) -> OperationResponse:
        while not data.done:
            time.sleep(3)
            response = self.session.get(
                url=f"{self.operation_base_url}/{data.id}",
                headers=headers,
            )
            data = OperationResponse.model_validate(response.json())

        return data


class IAMTokenBearerAuthClient(HTTPClient):
    def __init__(self, iam_token: str):
        super().__init__()
        self.session.headers["Authorization"] = f"Bearer {iam_token}"


class YCSecretClient(IAMTokenBearerAuthClient):
    base_url = "https://lockbox.api.cloud.yandex.net/lockbox/v1/secrets"

    def get(self, secret_id: str) -> SecretCreateOut:
        return self.request(
            url=f"{self.base_url}/{secret_id}",
            response_type=SecretCreateOut,
            is_operation=False,
        )

    def update(self, secret_id: str, data: SecretUpdateIn) -> SecretCreateOut:
        return self.request(
            url=f"{self.base_url}/{secret_id}",
            response_type=SecretCreateOut,
            method="patch",
            data=data,
        )

    def update_version(self, secret_id: str, data: SecretUpdateVersionIn) -> SecretUpdateVersionOut:
        return self.request(
            url=f"{self.base_url}/{secret_id}:addVersion",
            response_type=SecretUpdateVersionOut,
            method="post",
            data=data,
        )

    def delete(self, secret_id: str) -> None:
        self.request(
            url=f"{self.base_url}/{secret_id}",
            method="delete",
        )

    def create(self, data: SecretCreateIn) -> SecretCreateOut:
        return self.request(
            url=self.base_url,
            response_type=SecretCreateOut,
            method="post",
            data=data,
        )


class YCPayloadClient(IAMTokenBearerAuthClient):
    base_url = "https://payload.lockbox.api.cloud.yandex.net/lockbox/v1/secrets/{secret_id}/payload"

    def get(self, secret_id: str, version_id: str | None = None) -> list[Payload]:
        data = self.request(
            self.base_url.format(secret_id=secret_id),
            params={"versionId": version_id},
            is_operation=False,
        )
        return [Payload(**secret) for secret in data["entries"]]


class YCVaultClient:
    def __init__(self, iam_token: str):
        self.secret = YCSecretClient(iam_token)
        self.payload = YCPayloadClient(iam_token)

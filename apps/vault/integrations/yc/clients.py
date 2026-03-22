from typing import Any

import requests


from .schemas import (
    Base,
    SecretDataResponse,
    SecretUpdateData,
    SecretModifyResponse,
    SecretUpdateVersionData,
    SecretCreateResponse,
    SecretCreateData,
    Payload,
)



class HTTPClient:
    def __init__(self):
        self.session = requests.Session()

    def request[T](
        self,
        url: str,
        response_type: T = dict(),
        method: str = "get",
        data: Base | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> T:
        response = self.session.request(
            method,
            url,
            params,
            data and data.model_dump(),
            headers,
        )
        response.raise_for_status()
        return type(response_type)(**response.json())


class IAMTokenBearerAuthClient(HTTPClient):
    def __init__(self, iam_token: str):
        super().__init__()
        self.session.headers["Authorization"] = f"Bearer {iam_token}"


class YCSecretClient(IAMTokenBearerAuthClient):
    base_url = "https://lockbox.api.cloud.yandex.net/lockbox/v1/secrets"

    def get(self, secret_id: str) -> SecretDataResponse:
        return self.request(
            f"{self.base_url}/{secret_id}",
            SecretDataResponse,
        )

    def update(self, secret_id: str, data: SecretUpdateData) -> SecretModifyResponse:
        return self.request(
            f"{self.base_url}/{secret_id}",
            SecretModifyResponse,
            "patch",
            data,
        )

    def update_version(self, secret_id: str, data: SecretUpdateVersionData) -> SecretModifyResponse:
        return self.request(
            f"{self.base_url}/{secret_id}:addVersion",
            SecretModifyResponse,
            "post",
            data,
        )

    def delete(self, secret_id: str) -> SecretModifyResponse:
        return self.request(
            f"{self.base_url}/{secret_id}",
            SecretModifyResponse,
            "delete",
        )

    def create(self, data: SecretCreateData) -> SecretCreateResponse:
        return self.request(
            self.base_url,
            SecretCreateResponse,
            "post",
            data,
        )


class YCPayloadClient(IAMTokenBearerAuthClient):
    base_url = "https://lockbox.api.cloud.yandex.net/lockbox/v1/secrets/{secret_id}/payload"

    def get(self, secret_id: str, version_id: str | None = None) -> list[Payload]:
        data = self.request(
            self.base_url.format(secret_id=secret_id),
            params={"versionId": version_id},
        )
        return [Payload(secret) for secret in data["entries"]]


class YCVaultClient:
    def __init__(self, iam_token: str):
        self.secret = YCSecretClient(iam_token)
        self.payload = YCPayloadClient(iam_token)

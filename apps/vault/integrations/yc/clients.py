from apps.core.integrations.yc.clients import IAMTokenBearerAuthClient

from .schemas import (
    Payload,
    SecretCreateIn,
    SecretCreateOut,
    SecretUpdateIn,
    SecretUpdateVersionIn,
    SecretUpdateVersionOut,
)


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

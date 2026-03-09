import abc
import datetime
from typing import Any, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel
import requests


class Base(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)


class BaseSecretMetadata(Base):
    secret_id: str


class SecretMetadata(BaseSecretMetadata):
    version_id: str


class ErrorData(Base):
    code: int
    message: str
    details: list[dict[str, Any]]


class RequestData(Base):
    created_by: str
    modified_at: datetime.datetime
    done: bool
    error: ErrorData | None = None
    metadata: BaseSecretMetadata


class PasswordPayloadSpecification(Base):
    password_key: str | None = None
    length: int | None = None
    include_uppercase: bool | None = None
    include_lowercase: bool | None = None
    include_digits: bool | None = None
    include_punctuation: bool | None = None
    included_punctuation: str | None = None
    excluded_punctuation: str | None = None

    @model_validator(mode="after")
    def one_field_existing_validation(self) -> Self:
        if all([getattr(self, field) is None for field in self.model_fields_set]):
            raise ValueError("One of the fields must be specified")

        return self


class SecretCurrentVersion(Base):
    id: str
    secret_id: str
    created_at: datetime.datetime
    destroy_at: datetime.datetime
    description: str
    status: str
    payload_entry_keys: list[str]
    password_payload_specification: PasswordPayloadSpecification


class Payload(Base):
    key: str
    text_value: str | None = None
    binary_value: bytes | None = None

    @model_validator(mode="after")
    def existing_value_validation(self) -> Self:
        if self.text_value is None and self.binary_value is None:
            raise ValueError("Either 'text_value' or 'binary_value' must be specified")

        return self


class SecretDataResponse(Base):
    id: str
    folder_id: str
    created_at: datetime.datetime
    name: str
    description: str
    labels: dict[str, str]
    kms_key_id: str
    status: str
    current_version: SecretCurrentVersion
    deletion_protection: bool
    password_payload_specification: PasswordPayloadSpecification


class SecretModifyResponse(RequestData):
    response: SecretDataResponse


class SecretCreateResponse(SecretModifyResponse):
    metadata: SecretMetadata


class SecretUpdateData(Base):
    update_mask: str = ""
    name: str | None = None
    description: str | None = None
    labels: dict[str, str] | None = None
    deletion_protection: bool | None = None
    password_payload_specification: PasswordPayloadSpecification | None = None


class SecretCreateData(Base):
    folder_id: str
    name: str
    create_version: bool = True
    description: str | None = None
    labels: dict[str, str] | None = None
    kms_key_id: str | None = None
    version_description: str | None = None
    version_payload_entries: list[Payload] = Field(default_factory=list)
    deletion_protection: bool | None = None
    password_payload_specification: PasswordPayloadSpecification | None = None


class IPayloadService(Protocol):
    @abc.abstractmethod
    def get(self, secret_id: str, version_id: str | None = None) -> list[object]: ...


class ISecretService(Protocol):
    @abc.abstractmethod
    def get(self, secret_id: str) -> object: ...

    @abc.abstractmethod
    def update(self, secret_id: str, data: object) -> object: ...

    @abc.abstractmethod
    def delete(self, secret_id: str) -> object: ...

    @abc.abstractmethod
    def create(self, data: object) -> object: ...


class RequestService:
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
        return type(response_type)(**response.json())


class YCSecretService(RequestService):
    base_url = "https://lockbox.api.cloud.yandex.net/lockbox/v1/secrets"

    def __init__(self, iam_token: str):
        self.session = requests.Session(
            headers={
                "Authorization": f"Bearer {iam_token}",
            }
        )

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


class YCPayloadService(RequestService):
    base_url = "https://lockbox.api.cloud.yandex.net/lockbox/v1/secrets/{secret_id}/payload"

    def __init__(self, iam_token: str):
        self.session = requests.Session(
            headers={
                "Authorization": f"Bearer {iam_token}",
            }
        )

    def get(self, secret_id: str, version_id: str | None = None) -> list[Payload]:
        data = self.request(
            self.base_url.format(secret_id=secret_id),
            params={"versionId": version_id},
        )
        return [Payload(secret) for secret in data["entries"]]

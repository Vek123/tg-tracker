import datetime

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel


class Base(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        serialize_by_alias=True,
        extra="allow",
    )


class BaseSecretMetadata(Base):
    secret_id: str


class SecretMetadata(BaseSecretMetadata):
    version_id: str


class ErrorData(Base):
    code: int
    message: str
    details: list[dict[str, Any]]


class OperationResponse(Base):
    id: str
    created_by: str
    created_at: datetime.datetime
    modified_at: datetime.datetime
    done: bool
    error: ErrorData | None = None
    metadata: BaseSecretMetadata
    description: str
    response: dict[str, Any] | None = None


class SecretCurrentVersion(Base):
    secret_id: str
    payload_entry_keys: list[str]


class Payload(Base):
    key: str
    text_value: str | None = None
    binary_value: bytes | None = None

    @model_validator(mode="after")
    def existing_value_validation(self) -> Self:
        if self.text_value is None and self.binary_value is None:
            raise ValueError("Either 'text_value' or 'binary_value' must be specified")

        return self


class SecretUpdateIn(Base):
    update_mask: str = ""
    name: str | None = None
    description: str | None = None
    labels: dict[str, str] | None = None
    deletion_protection: bool | None = None


class SecretUpdateVersionIn(Base):
    payloadEntries: list[Payload]
    description: str | None = None
    baseVersionId: str | None = None


class SecretUpdateVersionOut(Base):
    payload_entry_keys: list[str]
    secret_id: str


class SecretCreateIn(Base):
    folder_id: str
    name: str
    create_version: bool = True
    version_payload_entries: list[Payload] = Field(default_factory=list)


class SecretCreateOut(Base):
    current_version: SecretCurrentVersion
    name: str

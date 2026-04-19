import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Base(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        serialize_by_alias=True,
        extra="allow",
    )


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
    description: str
    response: dict[str, Any] | None = None

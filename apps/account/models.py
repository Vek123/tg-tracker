from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.models import Model

if TYPE_CHECKING:
    from apps.ai.models import UserMcp


class LANGUAGES(PyEnum):
    RU = "ru"
    ENG = "eng"


class User(Model):
    __tablename__ = "user"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[LANGUAGES] = mapped_column(default=LANGUAGES.RU)
    previous_ai_response_id: Mapped[str | None] = mapped_column(default=None)
    mcp: Mapped["UserMcp"] = relationship(back_populates="user", foreign_keys="UserMcp.user_id", primaryjoin="User.tg_id == UserMcp.user_id")

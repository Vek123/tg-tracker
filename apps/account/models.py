from enum import Enum as PyEnum

from sqlalchemy.orm import Mapped, mapped_column

from apps.core.models import Model


class LANGUAGES(PyEnum):
    RU = "ru"
    ENG = "eng"


class User(Model):
    __tablename__ = "user"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[LANGUAGES] = mapped_column(default=LANGUAGES.RU)

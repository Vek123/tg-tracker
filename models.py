from enum import Enum as PyEnum

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class LANGUAGES(PyEnum):
    RU = "ru"
    ENG = "eng"


class Table(DeclarativeBase):
    pass


class User(Table):
    __tablename__ = "user"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[LANGUAGES] = mapped_column(default=LANGUAGES.RU)


class Fsm(Table):
    __tablename__ = "fsm"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]


class Secret(Table):
    __tablename__ = "secret"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    secret_id: Mapped[str]

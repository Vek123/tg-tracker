from sqlalchemy.orm import Mapped, mapped_column

from apps.core.models import Model


class Fsm(Model):
    __tablename__ = "fsm"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]

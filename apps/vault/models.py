from sqlalchemy.orm import Mapped, mapped_column

from apps.core.models import Model


class Secret(Model):
    __tablename__ = "secret"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    secret_id: Mapped[str]

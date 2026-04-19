from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.account.models import User
from apps.core.models import Model


class UserMcp(Model):
    __tablename__ = "user_mcp"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    user: Mapped[User] = relationship(back_populates="mcp", foreign_keys="UserMcp.user_id", primaryjoin="UserMcp.user_id == User.tg_id")
    mcp_gateway_id: Mapped[str] = mapped_column(String(64))
    mcp_base_url: Mapped[str] = mapped_column(String(256))

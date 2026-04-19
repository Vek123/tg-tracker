from typing import Tuple

from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from ..models import UserMcp

class UserMcpService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, mcp_gateway_id: str, mcp_base_url: str) -> UserMcp:
        mcp = UserMcp(user_id=user_id, mcp_gateway_id=mcp_gateway_id, mcp_base_url=mcp_base_url)
        self.session.add(mcp)
        self.session.commit()
        return mcp

    def delete(self, user_id: int) -> None:
        stmt = delete(UserMcp).where(UserMcp.user_id == user_id)
        self.session.execute(stmt)
        self.session.commit()

    def get(self, user_id: int) -> UserMcp | None:
        stmt = select(UserMcp).where(UserMcp.user_id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_or_create(self, user_id: int, mcp_gateway_id: str, mcp_base_url: str) -> Tuple[bool, UserMcp]:
        mcp = self.get(user_id)
        created = False
        if mcp is None:
            mcp = self.create(user_id, mcp_gateway_id, mcp_base_url)
            created = True

        return created, mcp

    def update(self, user_id: int, mcp_gateway_id: str, mcp_base_url: str) -> None:
        stmt = update(UserMcp).where(UserMcp.user_id == user_id).values(mcp_gateway_id=mcp_gateway_id, mcp_base_url=mcp_base_url)
        self.session.execute(stmt)
        self.session.commit()

from apps.ai.integrations.yc.schemas import McpCreateIn, McpGet, McpUpdateIn
import settings

from .clients import McpClient
from .tools.tracker import get_personal_create_tools, McpTrackerData


class TrackerMcpRepository:
    def __init__(self, client: McpClient):
        self.client = client

    def create(self, data: McpTrackerData, user_id: int) -> McpGet:
        payload = McpCreateIn(
            folder_id=settings.YC_FOLDER_ID,
            name=f"tracker-{user_id}",
            service_account_id=settings.SA_KEY.service_account_id,
            public=False,
            tools=get_personal_create_tools(data),
        )
        return self.client.create(payload)

    def update(self, data: McpTrackerData, mcp_gateway_id: str) -> McpGet:
        payload = McpUpdateIn(
            update_mask="tools",
            tools=get_personal_create_tools(data),
        )
        return self.client.update(mcp_gateway_id=mcp_gateway_id, data=payload)

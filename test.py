from apps.ai.integrations.yc.clients import McpClient
from apps.ai.integrations.yc.repositories import TrackerMcpRepository
from apps.ai.integrations.yc.tools.tracker import McpTrackerData
import settings


mcp = TrackerMcpRepository(McpClient(settings.IAM_TOKEN)).create(
    data=McpTrackerData(secret_id="e6q2lvpaup2u0ltdg1jt", token_key_name="token", org_id_key_name="org_id"),
    user_id=1284471608,
)

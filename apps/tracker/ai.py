
from openai.types.responses.response_output_item import McpApprovalRequest

from apps.ai.models import UserMcp
import settings

from apps.ai.integrations.yc.tools.tracker import get_personal_use_tools

from apps.ai.dialog import ApproveRequest, Chat


class AITrackerHelper:
    def __init__(
        self,
        user_mcp: UserMcp,
        previous_response_id: str | None = None,
    ):
        self._chat = Chat(
            model_url=settings.YC_AI_MODEL_URL,
            tools=get_personal_use_tools(mcp_url=user_mcp.mcp_url),
            previous_response_id=previous_response_id,
        )

    def message(self, text: str) -> str | list[McpApprovalRequest] | None:
        return self._chat.message(text)

    def approve_requests(self, requests: list[ApproveRequest]) -> str | list[ApproveRequest] | None:
        return self._chat.approve_mcp_requests(requests=requests)

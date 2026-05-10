from openai.types.responses.response_output_item import McpApprovalRequest

from apps.account.models import User

import settings

from apps.ai.integrations.yc.tools.tracker import get_personal_use_tools

from apps.ai.dialog import ApproveRequest, Chat

from sqlalchemy.orm import Session


class AITrackerHelper:
    def __init__(
        self,
        user: User,
        db_session: Session,
    ):
        self.user = user
        self.db_session = db_session
        self.chat = Chat(
            model_url=settings.YC_AI_MODEL_URL,
            tools=get_personal_use_tools(mcp_url=user.mcp.mcp_base_url),
            previous_response_id=user.previous_ai_response_id,
        )

    def handle_response(self, response: str | list[McpApprovalRequest] | None) -> str | list[ApproveRequest] | None:
        self.user.previous_ai_response_id = self.chat.previous_response_id
        self.db_session.commit()
        if isinstance(response, list):
            return self.build_approve_requests(response)

        return response

    def message(self, text: str) -> str | list[ApproveRequest] | None:
        response = self.chat.message(text)
        return self.handle_response(response)

    def approve_requests(self, requests: list[ApproveRequest]) -> str | list[ApproveRequest] | None:
        response = self.chat.approve_mcp_requests(requests=requests)
        return self.handle_response(response)

    def build_approve_requests(self, requests: list[McpApprovalRequest]) -> ApproveRequest:
        return [
            ApproveRequest(
                id=request.id,
                title=f"Название: {request.name}, параметры: {request.arguments}",
            )
            for request in requests
        ]

from openai import OpenAI

import settings

from apps.ai.dialog import ApproveRequest, Chat


class AITrackerHelper:
    def __init__(
        self,
        mcp_url: str,
        previous_response_id: str | None = None
    ):
        self._chat = Chat(
            client=OpenAI(
                api_key=settings.IAM_TOKEN,
                base_url="https://ai.api.cloud.yandex.net/v1",
                project=settings.YC_FOLDER_ID,
                previous_response_id=previous_response_id,
            ),
            model_url=settings.YC_AI_MODEL_URL,
            tools=[
                {
                    "server_label": "tracker",
                    "type": "mcp",
                    "headers": {"Authorization": f"Bearer {settings.IAM_TOKEN}"},
                    "server_url": mcp_url,  # "https://db86q8j6k5935lernk0q.99igvxy3.mcpgw.serverless.yandexcloud.net/sse"
                },
            ],
        )

    def message(self, text: str) -> str | list[ApproveRequest] | None:
        return self._chat.message(text)

    def approve_requests(self, requests: list[ApproveRequest]) -> str | list[ApproveRequest] | None:
        return self._chat.approve_mcp_requests(requests=requests)

import base64
import json

import filetype

from apps.core.integrations.yc.clients import IAMTokenBearerAuthClient
import settings

from .schemas import McpCreateIn, McpGet, McpUpdateIn, SpeechKitAudioFormat, SpeechKitContainerAudio, SpeechKitRecognitionModel, SpeechKitRecognizeIn


class McpClient(IAMTokenBearerAuthClient):
    base_url = "https://serverless-mcp-gateway.api.cloud.yandex.net/mcpgateway/v1/mcpGateways"

    def create(self, data: McpCreateIn) -> McpGet:
        return self.request(
            url=self.base_url,
            method="post",
            data=data,
            response_type=McpGet,
        )

    def delete(self, mcp_gateway_id: str) -> None:
        self.request(
            url=f"{self.base_url}/{mcp_gateway_id}",
            method="delete",
        )

    def update(self, mcp_gateway_id: str, data: McpUpdateIn) -> McpGet:
        return self.request(
            url=f"{self.base_url}/{mcp_gateway_id}",
            method="patch",
            data=data,
            response_type=McpGet,
        )

    def get(self, mcp_gateway_id: str) -> McpGet:
        return self.request(
            url=f"{self.base_url}/{mcp_gateway_id}",
            method="get",
            response_type=McpGet,
            is_operation=False,
        )


class SpeechKitClient(IAMTokenBearerAuthClient):
    base_url = "https://stt.api.cloud.yandex.net/stt/v3"

    def _get_container_audio_type(self, audio: bytes, mime_type: str | None = None) -> str:
        if not mime_type:
            try:
                mime_type = filetype.guess_mime(audio)
            except TypeError:
                return "CONTAINER_AUDIO_TYPE_UNSPECIFIED"

        mime_type = mime_type.lower().strip()
        if mime_type.endswith("mpeg"):
            return "MP3"
        elif mime_type.endswith("wav"):
            return "WAV"
        elif mime_type.endswith("ogg"):
            return "OGG_OPUS"

        return "CONTAINER_AUDIO_TYPE_UNSPECIFIED"

    def recognize(self, audio: bytes, mime_type: str | None = None) -> None:
        response = self.request(
            url=f"{self.base_url}/recognizeFileAsync",
            method="post",
            data=SpeechKitRecognizeIn(
                content=base64.b64encode(audio).decode(),
                recognition_model=SpeechKitRecognitionModel(
                    model="general",
                    audio_format=SpeechKitAudioFormat(
                        container_audio=SpeechKitContainerAudio(
                            container_audio_type=self._get_container_audio_type(audio, mime_type),
                        ),
                    ),
                ),
            ),
        )
        return response

    def get_recognition(self, operation_id: str) -> dict:
        response = self.request(
            url=f"{self.base_url}/getRecognition?operation_id={operation_id}",
            method="get",
            is_operation=False,
            response_builder=lambda body: [json.loads(line) for line in body.decode().strip().split("\n")]
        )
        return response

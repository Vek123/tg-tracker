import abc

from dataclasses import dataclass
from typing import Any

from openai import OpenAI
from openai.types.responses import Response
from openai.types.responses.response_output_item import McpApprovalRequest

from logger import logger


class IChat(abc.ABC):
    @abc.abstractmethod
    def message(self, text: str, files: list[str] | None = None, auto_approve: bool = False) -> str | list[McpApprovalRequest] | None:
        ...

    @abc.abstractmethod
    def clear_chat(self) -> None:
        ...


@dataclass
class ApproveRequest:
    id: str
    approve: bool = False


class Chat(IChat):
    def __init__(
        self,
        client: OpenAI,
        model_url: str,
        tools: list[dict[str, Any]] | None = None,
        developer_input: list[str] | None = None,
        previous_response_id: str | None = None,
    ):
        self.client = client
        self.model_url = model_url
        self.tools = tools
        self.developer_input = self._build_developer_input(developer_input)
        self.previous_response_id = previous_response_id
        logger.info("Chat instance successfully initialized")

    def _build_developer_input(self, developer_input: list[str] | None) -> list[dict[str, Any]] | None:
        if not developer_input:
            return []

        return [{"role": "developer", "content": text} for text in developer_input]

    def _handle_response(self, response: Response) -> str | list[McpApprovalRequest] | None:
        self.previous_response_id = response.id
        if response.error:
            logger.error("Response contains an error")
            logger.error(response.error.message)
            return None

        approve: list[McpApprovalRequest] = []
        for output in response.output:
            if isinstance(output, McpApprovalRequest):
                approve.append(output)
            elif output.type == "message":
                texts = []
                for content in output.content:
                    if content.type == "output_text":
                        texts.append(content.text)

                if texts:
                    logger.info("Response contains text")
                    return "".join(texts)

        if approve:
            logger.info("Response contains approval requests")

        return approve or None

    def _build_request(
        self,
        text: str | None = None,
        files: list[str] | None = None,
        approval_requests: list[ApproveRequest] | None = None,
    ) -> dict[str, Any]:
        content = []
        if text:
            content.append({"type": "input_text", "text": text})

        if files:
            content.extend([{
                "type": "input_file",
                "file_url": file_url,
            } for file_url in files])

        input_data = self.developer_input if not self.previous_response_id else []
        if content:
            input_data.append({
                "role": "user",
                "content": content,
            })

        data = {
            "input": input_data,
            "previous_response_id": self.previous_response_id,
            "model": self.model_url,
            "tools": self.tools,
        }
        if approval_requests:
            input_data.extend([{
                "type": "mcp_approval_response",
                "approve": request.approve,
                "approval_request_id": request.id,
            } for request in approval_requests])

        logger.info("Request was built")
        return data

    def approve_mcp_requests(self, requests: list[ApproveRequest]) -> Response:
        response = self.client.responses.create(
            **self._build_request(approval_requests=requests),
        )
        if response.error:
            logger.error("Error was occured while approving requests")
            logger.error(response.error.message)
        else:
            logger.info("Requests was successfully approved")

        return response

    def message(self, text: str, files: list[str] | None = None, auto_approve: bool = False):
        logger.info("Sending message...")
        response = self.client.responses.create(
            **self._build_request(text, files),
        )
        logger.info("Response received")
        while True:
            processed_response = self._handle_response(response)
            if not processed_response:
                return None
            elif isinstance(processed_response, str):
                return processed_response

            if not auto_approve:
                break
            else:
                response = self.approve_mcp_requests([ApproveRequest(request.id, True) for request in processed_response])

        return processed_response

    def clear_chat(self) -> None:
        self.previous_response_id = None

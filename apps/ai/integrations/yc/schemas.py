import datetime
import http

from typing import Any, Literal

from pydantic import Field, field_serializer, field_validator

from apps.core.integrations.yc.schemas import Base


class ForwardHeadersPolicy(Base):
    mode: Literal["WHITE_LIST", "BLACK_LIST"] = "WHITE_LIST"
    headers: list[str]


class FunctionCall(Base):
    function_id: str
    tag: str | None = None


class ToolCall(Base):
    tool_name: str
    parameters_json: str | None = None


class HeaderAuthorization(Base):
    header_name: str
    header_value: str


class ContainerCall(Base):
    container_id: str
    path: str | None = None
    method: http.HTTPMethod = http.HTTPMethod.GET
    body: str | None = None
    headers: dict[str, str] | None = None
    query: dict[str, str] | None = None
    forward_headers: ForwardHeadersPolicy | None = None


class HttpCall(Base):
    url: str
    method: http.HTTPMethod = http.HTTPMethod.GET
    body: str | None = None
    headers: dict[str, str] | None = None
    query: dict[str, str] | None = None
    use_service_account: bool = True
    forward_headers: ForwardHeadersPolicy | None = None


class McpCall(Base):
    url: str
    tool_call: ToolCall
    transport: Literal["SSE", "SSE"] = "SSE"
    unauthorized: dict | None = None
    header: HeaderAuthorization | None = None
    service_account: dict[str, Any] | None = None
    forward_headers: dict[str, str] | None = None
    transfer_headers: ForwardHeadersPolicy | None = None


class GrpcCall(Base):
    endpoint: str
    method: str
    use_service_account: bool = True
    body: str | None = None
    headers: dict[str, str] | None = None
    forward_headers: ForwardHeadersPolicy | None = None


McpAction = FunctionCall | ToolCall | ContainerCall | HttpCall | McpCall | GrpcCall
McpActions_map = {
    "functionCall": FunctionCall,
    "toolCall": ToolCall,
    "containerCall": ContainerCall,
    "httpCall": HttpCall,
    "mcpCall": McpCall,
    "grpcCall": GrpcCall,
}


class McpTool(Base):
    name: str
    description: str | None = None
    input_json_schema: str
    action: McpAction

    @field_serializer("action")
    def serialize_action(self, value: McpAction) -> dict[str, McpAction]:
        call_name = value.__class__.__name__
        call_name = call_name[0].lower() + call_name[1:]
        return {call_name: value}

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, value: Any) -> McpAction:
        if isinstance(value, dict):
            action_name = list(value.keys())[0]
            action_class = McpActions_map.get(action_name)
            if action_class:
                return action_class(**value[action_name])

            raise ValueError(f"Unknown action type: {action_name}")

        return value


class McpCreateIn(Base):
    folder_id: str
    name: str
    service_account_id: str
    public: bool = True
    tools: list[McpTool] = Field(default_factory=list, min_length=1)
    description: str | None = None


class McpUpdateIn(McpCreateIn):
    update_mask: str


class McpGet(McpCreateIn):
    id: str
    created_at: datetime.datetime
    status: str
    base_domain: str
    cloud_id: str

    @property
    def url(self) -> str:
        return f"{self.base_domain}/sse"


class McpDeleteOut(Base):
    mcp_gateway_id: str

from apps.core.integrations.yc.clients import IAMTokenBearerAuthClient

from .schemas import McpCreateIn, McpGet, McpUpdateIn


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

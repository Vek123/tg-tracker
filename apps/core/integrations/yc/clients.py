import time
import requests

from typing import Any

from .schemas import Base, OperationResponse


class HTTPClient:
    operation_base_url = "https://operation.api.cloud.yandex.net/operations"

    def __init__(self):
        self.session = requests.Session()

    def request[T](
        self,
        url: str,
        response_type: T | None = None,
        method: str = "get",
        data: Base | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        is_operation: bool = True,
    ) -> T:
        if response_type is None:
            response_type = dict

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data and data.model_dump(),
            headers=headers,
        )
        response.raise_for_status()
        if is_operation:
            response = OperationResponse.model_validate(response.json())
            response = self.wait_operation(response, headers)
            return response_type(**response.response)

        return response_type(**response.json())

    def wait_operation(self, data: OperationResponse, headers: dict[str, Any]) -> OperationResponse:
        while not data.done:
            time.sleep(3)
            response = self.session.get(
                url=f"{self.operation_base_url}/{data.id}",
                headers=headers,
            )
            data = OperationResponse.model_validate(response.json())

        return data


class IAMTokenBearerAuthClient(HTTPClient):
    def __init__(self, iam_token: str):
        super().__init__()
        self.session.headers["Authorization"] = f"Bearer {iam_token}"

from copy import deepcopy
from dataclasses import dataclass
from typing import Iterable

from openai.types.responses.tool import Tool, Mcp

import settings

from ..schemas import HeaderAuthorization, McpCall, McpTool, ToolCall


@dataclass
class McpTrackerData:
    secret_id: str
    token_key_name: str
    org_id_key_name: str


def get_personal_create_tools(data: McpTrackerData) -> tuple[McpTool]:
    tools = deepcopy(CreateMcpToolsPayload)
    for tool in tools:
        tool.action.forward_headers["x-cloud-org-id"] = f"\\(lockboxPayload(\"{data.secret_id}\"; \"{data.org_id_key_name}\"))"
        tool.action.header.header_value = f"\\(lockboxPayload(\"{data.secret_id}\"; \"{data.token_key_name}\"))"

    return tools


def get_personal_use_tools(mcp_url: str) -> Iterable[Tool]:
    tools = deepcopy(UseMcpToolsPayload)
    for tool in tools:
        tool.server_url = mcp_url

    return tools


UseMcpToolsPayload: Iterable[Tool] = (
    Mcp(
        type="mcp",
        server_label="tracker",
        server_url="fake",
        headers={
            "Authorization": f"Bearer {settings.IAM_TOKEN}",
        },
    ),
)


CreateMcpToolsPayload: Iterable[McpTool] = (
    McpTool(
        name="GetIssue",
        description="Get Issue by issue key",
        input_json_schema="{\"properties\":{\"comments_limit\":{\"anyOf\":[{\"type\":\"integer\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Number of most recent comments to include. If set to 0, no comments will be returned. Use this to reduce response size and save context.\",\"title\":\"Comments Limit\"},\"fields\":{\"anyOf\":[{\"items\":{\"type\":\"string\"},\"type\":\"array\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"List of fields to include in the response. If not specified, all fields will be returned. Use ['key'] to get just the issue key or ['summary', 'description'] to get just the summary and description to reduce response size and save context.\",\"title\":\"Fields\"},\"key\":{\"description\":\"Issue key\",\"title\":\"Key\",\"type\":\"string\"}},\"required\":[\"key\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="GetIssueLinks",
        description="Get Issue Links by issue key",
        input_json_schema="{\"properties\":{\"key\":{\"description\":\"Issue key\",\"title\":\"Key\",\"type\":\"string\"}},\"required\":[\"key\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="GetIssues",
        description="Get issues by filters such as status, assignee, queue, tags, or by raw query.\n\nYou must provide either a `filter` (dictionary of structured filters) or a `query` (a free-form search query in Yandex Tracker Query Language).\n\nThe result may be paginated. If the total number of issues is large, the response will include:\n- `page`: current page number\n- `pages_count`: total number of pages\n- `issues`: list of issues for this page\n\nTo fetch all matching issues, you must call this tool multiple times with increasing `page` number, e.g., page=1, page=2, ..., until `page` == `pages_count`.\nSet `per_page` to control the number of issues per page (recommended is 50).\n\nYou can also limit the response size using:\n- `fields`: list of fields to include in each issue (default is ['key'])\n- `comments_limit`: how many recent comments to return per issue (0 by default — no comments)\n\n",
        input_json_schema="{\"properties\":{\"comments_limit\":{\"default\":0,\"description\":\"Number of most recent comments to include.\\nIf set to 0, no comments will be returned.\\nUse this to reduce response size and save context.\\nIf not set, the full comment history will be included.\",\"title\":\"Comments Limit\",\"type\":\"integer\"},\"fields\":{\"default\":[\"key\"],\"description\":\"List of fields to include in the response.\\nUse ['key'] to get just the issue key or ['summary', 'description'] to reduce response size.\\nIf not specified, all available fields will be returned.\\nCommon field names include: 'summary', 'description', 'status', 'type', 'priority', 'assignee', 'createdBy'.\",\"items\":{\"type\":\"string\"},\"title\":\"Fields\",\"type\":\"array\"},\"filter\":{\"anyOf\":[{\"additionalProperties\":true,\"type\":\"object\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Dictionary with filter parameters. Ignored if `query` is provided.\\n\\nExample:\\n  {\\\"statusType\\\": \\\"open\\\", \\\"assignee\\\": \\\"me()\\\", \\\"queue\\\": [\\\"CORE\\\"]}\\n\\nAvailable keys:\\n- statusType: list of statuses or alias 'open'. Available values:\\n    'new', 'inProgress', 'paused', 'cancelled', 'done'\\n- assignee: login or me()\\n- queue: list of queue keys (e.g., ['CORE', 'TEST'])\\n- tags: list of tags (e.g., ['urgent'])\\n- created_from / created_to: ISO-8601 dates (e.g., '2024-01-01')\\n- updated_from / updated_to: ISO-8601 dates\\n\\nUse this when you want to build structured filters without writing query manually.\",\"title\":\"Filter\"},\"order\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Sort direction and field (ONLY with `filter`). Format: [+/-]\\u003cfield_key\\u003e, where '+' is ascending and '-' is descending. Example: '+createdAt', '-updated'.\",\"title\":\"Order\"},\"page\":{\"anyOf\":[{\"type\":\"integer\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Page number to retrieve (starts from 1).\\nUse together with `per_page` for paginated access.\\nIf the result set is large and `page` is not specified, automatic pagination will be triggered starting from page 1.\\nTo fetch all issues, iterate through pages from 1 to `pages_count` (returned in the response).\\nFor example:\\n  { \\\"page\\\": 1, \\\"per_page\\\": 20 }\\n  { \\\"page\\\": 2, \\\"per_page\\\": 20 }\\n  ...\\n  Stop when `page` equals `pages_count`.\",\"title\":\"Page\"},\"per_page\":{\"anyOf\":[{\"type\":\"integer\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Number of issues per page (recommended is 20).\\nMaximum value depends on the Tracker API limits, typically between 20 and 100.\\nUse smaller values to reduce response size and avoid timeouts.\\nCombined with `page`, this enables pagination.\\nTo get all issues, iterate over pages until `page == pages_count`.\",\"title\":\"Per Page\"},\"query\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"A free-form filter query written in Yandex Tracker Query Language.\\n\\nIf this field is set, `filter` must be omitted.\\n\\nThis language allows flexible filtering based on issue fields. It supports logical operators, comparisons, functions, and grouping. Key syntax rules:\\n\\nBasic format: \\u003cfield\\u003e\\u003coperator\\u003e\\u003cvalue\\u003e, for example:\\n  - assignee:me() — issues assigned to the current user\\n  - status:inProgress — issues with 'inProgress' status\\n  - queue:CORE — issues from the CORE queue\\n  - created:\\u003e=2024-01-01 — issues created on or after Jan 1, 2024\\n  - priority:high — issues with high priority\\n\\nSupported comparison operators:\\n  - : — equals (e.g., status:open)\\n  - != — not equal (e.g., status!=done)\\n  - \\u003e / \\u003e= — greater / greater or equal (e.g., created:\\u003e2023-12-01)\\n  - \\u003c / \\u003c= — less / less or equal (e.g., updated:\\u003c2024-06-01)\\n\\nLogical operators:\\n  - AND — logical AND (e.g., status:open AND assignee:me())\\n  - OR — logical OR (e.g., queue:CORE OR queue:TEST)\\n  - NOT — negation (e.g., NOT tags:internal)\\n\\nGrouping: use parentheses to combine expressions:\\n  - (status:open OR status:inProgress) AND priority:high\\n\\nMultiple values:\\n  - tags:urgent OR tags:important — issues that have at least one of the tags\\n  - followers:me() — issues followed by the current user\\n\\nBuilt-in functions:\\n  - me() — current user (can be used with assignee, createdBy, followers, etc.)\\n  - today() — current date (e.g., updated:\\u003e=today())\\n\\nSorting results:\\nYou can sort filter results by appending a \\\"Sort By\\\" clause at the end of the query. Provide a field name to sort by:\\n  \\\"Sort By\\\": Created\\nOptionally specify sort order: ASC (ascending) or DESC (descending):\\n  \\\"Sort By\\\": Created ASC\\nTo sort by multiple fields, list them by priority, separated by commas:\\n  \\\"Sort By\\\": Created ASC, Updated DESC\\nExample scenarios:\\n  - All issues from queue CORE assigned to me:\\n      queue:CORE AND assignee:me()\\n  - Issues with tag urgent created in 2024, newest first by update time:\\n      tags:urgent AND created:\\u003e=2024-01-01 AND created:\\u003c=2024-12-31 \\\"Sort By\\\": Updated DESC\\n  - Open issues excluding queue TEST, oldest first by creation date:\\n      status!=done AND NOT queue:TEST \\\"Sort By\\\": Created ASC\\nFull syntax guide: https://yandex.ru/support/tracker/ru/user/query-filter\",\"title\":\"Query\"}},\"required\":[],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="GetProject",
        description="Fetch a project by key",
        input_json_schema="{\"properties\":{\"key\":{\"description\":\"Key of the object to fetch\",\"title\":\"Key\",\"type\":\"string\"}},\"required\":[\"key\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="GetPortfolio",
        description="Fetch a portfolio by key",
        input_json_schema="{\"properties\":{\"key\":{\"description\":\"Key of the object to fetch\",\"title\":\"Key\",\"type\":\"string\"}},\"required\":[\"key\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="GetGoal",
        description="Fetch a goal by key",
        input_json_schema="{\"properties\":{\"key\":{\"description\":\"Key of the object to fetch\",\"title\":\"Key\",\"type\":\"string\"}},\"required\":[\"key\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="SearchEntities",
        description="Search entities (project, goal, portfolio) by filters or text",
        input_json_schema="{\"properties\":{\"entity_type\":{\"description\":\"Entity type to search: 'project', 'goal', 'portfolio', etc.\",\"title\":\"Entity Type\",\"type\":\"string\"},\"fields\":{\"anyOf\":[{\"items\":{\"type\":\"string\"},\"type\":\"array\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"List of fields to include in response. Available only these fields: 'summary', 'description', 'author', 'lead', 'teamUsers', 'clients', 'followers', 'start', 'end', 'checklistItems', 'tags', 'parentEntity', 'teamAccess', 'quarter', 'entityStatus'. If requesting entityStatus, possible values for projects and portfolios are: 'draft' for new, 'draft2' for draft, 'in_progress', 'launched', 'postponed', 'at_risk', 'blocked', 'according_to_plan', 'cancelled'. For goals, possible values are: 'draft', 'according_to_plan', 'at_risk', 'blocked', 'achieved', 'partially_achieved', 'not_achieved', 'exceeded', 'cancelled'.\",\"title\":\"Fields\"},\"filter\":{\"anyOf\":[{\"additionalProperties\":true,\"type\":\"object\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Optional filtering, e.g., {'status': 'active'}\",\"title\":\"Filter\"},\"order_asc\":{\"anyOf\":[{\"type\":\"boolean\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Sort ascending (true) or descending (false)\",\"title\":\"Order Asc\"},\"order_by\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Field to sort by\",\"title\":\"Order By\"},\"page\":{\"default\":1,\"description\":\"Page number\",\"title\":\"Page\",\"type\":\"integer\"},\"per_page\":{\"default\":50,\"description\":\"Number of items per page\",\"title\":\"Per Page\",\"type\":\"integer\"},\"root_only\":{\"anyOf\":[{\"type\":\"boolean\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Return only root elements\",\"title\":\"Root Only\"},\"search_string\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Free-text search string (optional)\",\"title\":\"Search String\"}},\"required\":[\"entity_type\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="CreateGoal",
        description="Create a new goal entity",
        input_json_schema="{\"properties\":{\"description\":{\"description\":\"Goal description\",\"title\":\"Description\",\"type\":\"string\"},\"entityStatus\":{\"default\":\"draft\",\"description\":\"Goal status\",\"title\":\"Entitystatus\",\"type\":\"string\"},\"links\":{\"anyOf\":[{\"items\":{\"additionalProperties\":true,\"type\":\"object\"},\"type\":\"array\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"List of links to other entities (projects, portfolios, goals). Each link should be a dictionary with:\\n- 'relationship': The relationship type. Available types:\\n  - 'DEPENDS_ON': current goal depends on the linked entity\\n  - 'IS_DEPENDENT_BY': current goal blocks the linked entity\\n  - 'RELATES': relates to the linked entity\\n  - 'PARENT_ENTITY': linked entity is parent\\n  - 'CHILD_ENTITY': linked entity is child\\n  - 'WORKS_TOWARDS': works towards the linked goal\\n  - 'IS_SUPPORTED_BY': is supported by the linked project/portfolio\\n- 'entity': The key/ID of the entity to link to\\n\\nExamples:\\n- [{'relationship': 'IS_SUPPORTED_BY', 'entity': 'PROJECT-123'}]\\n- [{'relationship': 'IS_SUPPORTED_BY', 'entity': '68500cf39ebd9c43b298f186'}]\\n- [{'relationship': 'DEPENDS_ON', 'entity': 'goal-456'}, {'relationship': 'IS_SUPPORTED_BY', 'entity': 'PROJECT-789'}]\",\"title\":\"Links\"},\"parentEntity\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Parent goal key (only goals can be parents of goals)\",\"title\":\"Parententity\"},\"summary\":{\"description\":\"Goal summary/title\",\"title\":\"Summary\",\"type\":\"string\"},\"tags\":{\"anyOf\":[{\"items\":{\"type\":\"string\"},\"type\":\"array\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Tags for the goal\",\"title\":\"Tags\"}},\"required\":[\"summary\",\"description\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="UpdateGoal",
        description="Update fields of a goal",
        input_json_schema="{\"properties\":{\"fields\":{\"additionalProperties\":true,\"description\":\"Dictionary of field values to update for the goal.\",\"title\":\"Fields\",\"type\":\"object\"},\"goal_key\":{\"description\":\"Goal key to update\",\"title\":\"Goal Key\",\"type\":\"string\"}},\"required\":[\"goal_key\",\"fields\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="DeleteGoal",
        description="Delete a goal by key",
        input_json_schema="{\"properties\":{\"goal_key\":{\"description\":\"Goal key to delete\",\"title\":\"Goal Key\",\"type\":\"string\"}},\"required\":[\"goal_key\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="CreateIssue",
        description="Create a new issue in specified queue",
        input_json_schema="{\"properties\":{\"description\":{\"description\":\"Issue description\",\"title\":\"Description\",\"type\":\"string\"},\"parent\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Parent issue key (optional)\",\"title\":\"Parent\"},\"priority\":{\"default\":\"normal\",\"description\":\"Issue priority (e.g., 'normal', 'high', 'low')\",\"title\":\"Priority\",\"type\":\"string\"},\"queue\":{\"description\":\"Queue key where to create the issue\",\"title\":\"Queue\",\"type\":\"string\"},\"summary\":{\"description\":\"Issue summary/title\",\"title\":\"Summary\",\"type\":\"string\"},\"type\":{\"description\":\"Issue type (e.g., 'task', 'bug', 'feature')\",\"title\":\"Type\",\"type\":\"string\"}},\"required\":[\"queue\",\"summary\",\"description\",\"type\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="CreateComment",
        description="Add a comment to an issue",
        input_json_schema="{\"properties\":{\"issue_key\":{\"description\":\"Issue key to add comment to\",\"title\":\"Issue Key\",\"type\":\"string\"},\"text\":{\"description\":\"Comment text content\",\"title\":\"Text\",\"type\":\"string\"}},\"required\":[\"issue_key\",\"text\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="ChangeIssueStatus",
        description="Change the status of an issue",
        input_json_schema="{\"properties\":{\"comment\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Optional comment\",\"title\":\"Comment\"},\"issue_key\":{\"description\":\"Issue key to change status of\",\"title\":\"Issue Key\",\"type\":\"string\"},\"resolution\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Optional resolution\",\"title\":\"Resolution\"},\"status\":{\"description\":\"Target status key (e.g., 'inProgress', 'close')\",\"title\":\"Status\",\"type\":\"string\"}},\"required\":[\"issue_key\",\"status\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="UpdateIssue",
        description="Update fields of an issue",
        input_json_schema="{\"properties\":{\"fields\":{\"additionalProperties\":true,\"description\":\"Dictionary of field values to update for the issue.\",\"title\":\"Fields\",\"type\":\"object\"},\"issue_key\":{\"description\":\"Issue key to update\",\"title\":\"Issue Key\",\"type\":\"string\"}},\"required\":[\"issue_key\",\"fields\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="BulkUpdate",
        description="Bulk update only for issues. Call WaitForBulkChange with returned bulkchange_id to wait for completion.",
        input_json_schema="{\"properties\":{\"issues\":{\"description\":\"List of issue keys\",\"items\":{\"type\":\"string\"},\"title\":\"Issues\",\"type\":\"array\"},\"values\":{\"additionalProperties\":true,\"description\":\"Dictionary of field values to update for all specified issues.\",\"title\":\"Values\",\"type\":\"object\"}},\"required\":[\"issues\",\"values\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="BulkTransition",
        description="Bulk transition only for issues to a different status. Call WaitForBulkChange with returned bulkchange_id to wait for completion. Hint: you can try to change status of one issue to get the correct transition name for the bulk operation.",
        input_json_schema="{\"properties\":{\"issues\":{\"description\":\"List of issue keys\",\"items\":{\"type\":\"string\"},\"title\":\"Issues\",\"type\":\"array\"},\"transition\":{\"description\":\"Transition key to apply (e.g., 'startProgress', 'close')\",\"title\":\"Transition\",\"type\":\"string\"},\"values\":{\"anyOf\":[{\"additionalProperties\":true,\"type\":\"object\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Additional field values for the transition (if required)\",\"title\":\"Values\"}},\"required\":[\"issues\",\"transition\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="BulkMove",
        description="Bulk move only for issues. Call WaitForBulkChange with returned bulkchange_id to wait for completion.",
        input_json_schema="{\"properties\":{\"issues\":{\"description\":\"List of issue keys\",\"items\":{\"type\":\"string\"},\"title\":\"Issues\",\"type\":\"array\"},\"move_all_fields\":{\"default\":false,\"description\":\"Copy all custom fields to the new queue\",\"title\":\"Move All Fields\",\"type\":\"boolean\"},\"move_to_initial_status\":{\"default\":false,\"description\":\"Set issue to initial status in new queue\",\"title\":\"Move To Initial Status\",\"type\":\"boolean\"},\"queue\":{\"description\":\"Target queue key (e.g., 'CORE')\",\"title\":\"Queue\",\"type\":\"string\"},\"values\":{\"anyOf\":[{\"additionalProperties\":true,\"type\":\"object\"},{\"type\":\"null\"}],\"default\":null,\"description\":\"Additional field values for the move operation\",\"title\":\"Values\"}},\"required\":[\"issues\",\"queue\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="WaitForBulkChange",
        description="Wait until bulk change with given ID is complete.",
        input_json_schema="{\"properties\":{\"bulkchange_id\":{\"description\":\"Bulk change ID to wait for completion\",\"title\":\"Bulkchange Id\",\"type\":\"string\"}},\"required\":[\"bulkchange_id\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
    McpTool(
        name="BulkUpdateMetaEntities",
        description="Bulk update for project/goal/portfolio meta-entities using their keys/ids",
        input_json_schema="{\"properties\":{\"entity_type\":{\"description\":\"Meta-entity type: \\\"project\\\", \\\"goal\\\", or \\\"portfolio\\\"\",\"title\":\"Entity Type\",\"type\":\"string\"},\"meta_entities\":{\"description\":\"List of meta-entity keys, e.g. [\\\"project-1\\\", \\\"goal-3\\\"]\",\"items\":{\"type\":\"string\"},\"title\":\"Meta Entities\",\"type\":\"array\"},\"values\":{\"additionalProperties\":true,\"description\":\"Update payload object. May contain the following optional keys:\\n\\n- fields: updates to apply to each entity. Provide a dictionary of field updates (e.g., 'priority': {'key': 'high'}).\\n- comment: optional comment describing the changes\\n\\nExample:\\n{\\n  'fields': {\\n    'summary': 'Updated name',\\n    'priority': {'key': 'high'}\\n  },\\n  'comment': 'Bulk update via MCP'\\n}\",\"title\":\"Values\",\"type\":\"object\"}},\"required\":[\"entity_type\",\"meta_entities\",\"values\"],\"type\":\"object\"}",
        action=McpCall(
            url="https://bba11klgcd484rnls5kc.containers.yandexcloud.net/mcp",
            forward_headers={
                "x-cloud-org-id": "fake",
            },
            transport="SSE",
            tool_call=ToolCall(
                tool_name="GetIssue",
                parameters_json="\\( . )",
            ),
            header=HeaderAuthorization(
                header_name="token",
                header_value="fake",
            ),
        ),
    ),
)
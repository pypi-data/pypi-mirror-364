from typing import override

import bir_mcp
import langchain.tools

from ai_app.tools.base import BaseToolkit


class JiraToolkit(BaseToolkit):
    def __init__(
        self,
        token: str,
        url: str,
        api_version: int = 2,
        max_tool_output_length: int | None = None,
        **kwargs,  # The kwargs from JiraParameters, need to use them for tenacity manually instead of passing to atlassian.Jira.
    ):
        super().__init__()
        self.mcp = bir_mcp.atlassian.Atlassian(
            token=token, url=url, api_version=api_version, **kwargs
        )
        self.max_tool_output_length = max_tool_output_length

    @override
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        tools = [
            self.mcp.get_jira_issue_overview,
        ]
        tools = [
            bir_mcp.utils.to_langchain_tool(tool, max_output_length=self.max_tool_output_length)
            for tool in tools
        ]
        return tools

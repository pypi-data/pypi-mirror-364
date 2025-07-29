import re
import pydantic_core

from collections.abc import Sequence
from itertools import chain
from textwrap import dedent
from typing import Any, override

from mcp.server.auth.provider import OAuthAuthorizationServerProvider
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.fastmcp.tools import Tool
from mcp.server.fastmcp.utilities.types import Image
from mcp.server.streamable_http import EventStore
from mcp.types import (
    Content,
    TextContent,
)

from e2b_code_interpreter import Sandbox

class FastMCPBox(FastMCP):
    def __init__(
        self,
        name: str | None = None,
        instructions: str | None = None,
        auth_server_provider: OAuthAuthorizationServerProvider[Any, Any, Any] | None = None,
        event_store: EventStore | None = None,
        *,
        tools: list[Tool] | None = None,
        sandbox_config: dict[str, Any] | None = None,
        **settings: Any,
    ):
        self.tool_codes = {}
        self.e2b_config = sandbox_config

        super().__init__(
            name=name,
            instructions=instructions,
            auth_server_provider=auth_server_provider,
            event_store=event_store,
            tools=tools,
            **settings
        )

    def store_tool_code(self, tool_name:str, raw_code: str):
        code = self.prepare_sandbox_code(raw_code)
        self.tool_codes[tool_name] = code

    def clear_tool_code(self, tool_name:str):
        self.tool_codes[tool_name] = None

    @override
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Sequence[Content]:
        """Call a tool by name with arguments."""
        #context = self.get_context()
        tool_code = self.tool_codes[name]
        if tool_code is None:
            raise ToolError(f"Unknown tool: {name}")

        run_code = self.add_run_code(name, tool_code, arguments)
        # @todo init local sandbox with param
        sandbox = Sandbox()
        result = sandbox.run_code(run_code)

        converted_result = self._convert_to_content(result)
        return converted_result

    def prepare_sandbox_code(self, raw_code:str) -> str:
        code = re.sub(r'@mcp\.tool\(.*?\)\s+def', 'def', raw_code, flags=re.DOTALL)
        code = dedent(code)
        print("===  prepare_sandbox_code  ===")
        print(code)
        print("===  end  ===")
        return code

    def add_run_code(self, tool_name:str, code:str, arguments:dict[str, Any]) -> str:
        params_str = ', '.join(f"{k}={repr(v)}" for k, v in arguments.items())
        tool_exec = f"{tool_name}({params_str})"
        print(f"prepare_sandbox_run: run_sandbox_tool={tool_exec}")
        code = code + f"\n{tool_exec}"
        code = dedent(code)
        return code

    def _convert_to_content(self, result: Any,) -> Sequence[Content]:
        """Convert a result to a sequence of content objects."""
        if result is None:
            return []

        if isinstance(result, Content):
            return [result]

        if isinstance(result, Image):
            return [result.to_image_content()]

        if isinstance(result, list | tuple):
            return list(chain.from_iterable(
                _convert_to_content(item) for item in result))  # type: ignore[reportUnknownVariableType]

        if not isinstance(result, str):
            result = pydantic_core.to_json(result, fallback=str, indent=2).decode()

        return [TextContent(type="text", text=result)]
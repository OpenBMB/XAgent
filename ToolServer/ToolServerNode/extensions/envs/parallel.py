"""Opt-in Parallel Search MCP tools for a session's ToolServerNode."""

import asyncio
import math
import os
from pathlib import Path
import tempfile
import uuid
from urllib.parse import urlsplit

from httpx import AsyncClient
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import Implementation

from core.base import BaseEnv
from core.exceptions import ToolExecutionError
from core.register import toolwrapper


MCP_URL = "https://search.parallel.ai/mcp"
USER_AGENT = "XAgent/0.2 (+https://github.com/OpenBMB/XAgent)"
SESSION_FILE = Path(tempfile.gettempdir()) / ".xagent-parallel-session-id"


def _conversation_id():
    """Keep the research ID across restarts of this dedicated node container."""
    try:
        return str(uuid.UUID(SESSION_FILE.read_text().strip()))
    except FileNotFoundError:
        pass

    # Publish a complete file atomically, including when workers start together.
    # This file belongs to the container's writable layer, not a shared config
    # volume or the user's workspace. A new node starts with no session file.
    with tempfile.NamedTemporaryFile(
        mode="w", dir=SESSION_FILE.parent, prefix=".xagent-parallel-", delete=False,
    ) as state:
        temporary = state.name
        try:
            state.write(str(uuid.uuid4()))
            state.flush()
            os.fsync(state.fileno())
            try:
                os.link(temporary, SESSION_FILE)
            except FileExistsError:
                pass
        finally:
            os.unlink(temporary)
    # Invalid existing state is an error; never silently rotate a research ID.
    return str(uuid.UUID(SESSION_FILE.read_text().strip()))


def _error_text(error):
    # MCP transports can wrap the underlying error in nested task groups.
    children = getattr(error, "exceptions", None)
    if children:
        return "; ".join(_error_text(child) for child in children)
    return str(error) or type(error).__name__


@toolwrapper()
class ParallelEnv(BaseEnv):
    """Search the web and extract page content with Parallel Search MCP.

    Free anonymous search uses Fast mode. No Parallel account or API key is needed.
    """

    def __init__(self, config=None):
        super().__init__(config)
        self._timeout = self.config.dict().get("parallel", {}).get("timeout", 30)
        if (isinstance(self._timeout, bool)
                or not isinstance(self._timeout, (int, float))
                or not math.isfinite(self._timeout) or self._timeout <= 0):
            raise ValueError("parallel.timeout must be a positive number of seconds")
        # The manager creates a dedicated node for each /get_cookie research run.
        # Its registry owns this env; MCP reconnects and node restarts keep the ID.
        self._session_id = _conversation_id()

    async def _request(self, name, arguments):
        async with AsyncClient(
            headers={"User-Agent": USER_AGENT}, timeout=self._timeout,
            follow_redirects=False,
        ) as client:
            async with streamable_http_client(MCP_URL, http_client=client) as streams:
                async with ClientSession(
                    streams[0], streams[1],
                    client_info=Implementation(name="XAgent", version="0.2"),
                ) as session:
                    await session.initialize()
                    result = await session.call_tool(name, arguments)
                    text = "\n\n".join(
                        block.text for block in result.content if block.type == "text"
                    )
                    if result.isError:
                        raise ToolExecutionError(text or "Parallel returned a tool error")
                    if not text:
                        raise ToolExecutionError("Parallel returned no text content")
                    return text

    async def _call(self, name, arguments):
        arguments = {**arguments, "session_id": self._session_id}
        try:
            return await asyncio.wait_for(
                self._request(name, arguments), timeout=self._timeout,
            )
        except asyncio.TimeoutError as error:
            raise ToolExecutionError("Parallel request timed out") from error
        except Exception as error:
            raise ToolExecutionError("Parallel request failed: " + _error_text(error)) from error

    async def search(self, query: str, objective: str) -> str:
        """Search the web with Parallel and return source URLs and relevant excerpts.

        :param string query: A focused keyword search query, ideally 3-6 words.
        :param string objective: The information to find, including any preferred sources or freshness requirements.
        :return string: Search results with source URLs and excerpts. Use ParallelEnv_fetch to read a selected page in more detail.
        """
        if not query.strip() or not objective.strip():
            raise ToolExecutionError("query and objective must not be empty")
        return await self._call("web_search", {
            "objective": objective, "search_queries": [query],
        })

    async def fetch(self, url: str, objective: str = None) -> str:
        """Extract readable Markdown from one public HTTP or HTTPS page with Parallel.

        :param string url: The actual HTTP or HTTPS URL to read, for example a source returned by ParallelEnv_search.
        :param string? objective: The information to extract from the page, up to 200 characters. Omit to extract general page content.
        :return string: Page content and source URL in Markdown.
        """
        try:
            parsed = urlsplit(url)
        except ValueError as error:
            raise ToolExecutionError("url must be a valid HTTP or HTTPS URL") from error
        if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
            raise ToolExecutionError("url must be an HTTP or HTTPS URL without credentials")
        if objective is not None and len(objective) > 200:
            raise ToolExecutionError("fetch objective must be at most 200 characters")
        arguments = {"urls": [url]}
        if objective is not None:
            arguments["objective"] = objective
        return await self._call("web_fetch", arguments)

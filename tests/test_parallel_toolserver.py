"""Exercise the optional extension through ToolServer's loader and dispatcher.

The MCP SDK and HTTP transport are real; only the remote HTTP server is replaced.
No model inference, Docker daemon or embedding service is needed.
"""

import asyncio
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import uuid

import httpx
import pytest


ROOT = Path(__file__).resolve().parents[1]
NODE = ROOT / "ToolServer" / "ToolServerNode"
SEARCH_TEXT = "# Sources\nhttps://example.org/report\nA useful research excerpt."
FETCH_TEXT = "# Report\nSource: https://example.org/report\nDetailed page content."


@pytest.fixture
def runtime(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(NODE))
    monkeypatch.chdir(ROOT)
    from config import CONFIG
    from core.register import ToolRegister

    cfg = deepcopy(CONFIG.dict())
    cfg["toolregister"]["tool_creation_doc"] = str(NODE / "assets" / "HOW_TO_BUILD_NEW_TOOLS.md")
    cfg["filesystem"]["work_directory"] = str(tmp_path / "workspace")
    cfg["parallel"] = {"timeout": 2}
    cfg["enabled_extensions"] = []
    monkeypatch.setattr(CONFIG, "cfg", cfg)
    # Load the production HTTP endpoints without starting Docker/embedding setup.
    spec = importlib.util.spec_from_file_location("toolserver_node_main", NODE / "main.py")
    node = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(node)
    registries = []

    def register(enabled=True):
        cfg["enabled_extensions"] = ["extensions.envs.parallel"] if enabled else []
        registry = ToolRegister()
        registries.append(registry)
        node.app.tool_register = registry
        return registry

    yield node, register, cfg
    for registry in registries:
        asyncio.run(registry.envs["WebEnv"].client.aclose())


class MCPServer:
    def __init__(self, monkeypatch, mode="json"):
        from extensions.envs import parallel

        self.requests = []
        self.calls = []
        self.mode = mode
        self.started = asyncio.Event()
        self.cancelled = asyncio.Event()
        self.clients = []

        def client(**kwargs):
            assert kwargs.get("trust_env", True) is True
            assert kwargs["follow_redirects"] is False
            result = httpx.AsyncClient(transport=httpx.MockTransport(self.handle), **kwargs)
            self.clients.append(result)
            return result

        monkeypatch.setattr(parallel, "AsyncClient", client)

    async def handle(self, request):
        assert str(request.url) == "https://search.parallel.ai/mcp"
        assert request.headers["User-Agent"] == "XAgent/0.2 (+https://github.com/OpenBMB/XAgent)"
        assert "authorization" not in request.headers
        assert "x-api-key" not in request.headers
        self.requests.append(request)
        if request.method == "GET":
            return httpx.Response(405)
        if request.method == "DELETE":
            assert request.headers["mcp-session-id"]
            return httpx.Response(200)
        payload = json.loads(request.content)
        method = payload["method"]
        if method == "notifications/initialized":
            return httpx.Response(202)
        response = {"jsonrpc": "2.0", "id": payload["id"]}
        if method == "initialize":
            assert payload["params"]["clientInfo"]["name"] == "XAgent"
            result = {
                "protocolVersion": payload["params"]["protocolVersion"],
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fixture", "version": "1"},
            }
        elif method == "tools/list":
            result = {"tools": [
                {"name": name, "inputSchema": {"type": "object"}}
                for name in ("web_search", "web_fetch")
            ]}
        elif method == "tools/call":
            self.calls.append(payload["params"])
            if self.mode == "http_error":
                return httpx.Response(403, text="Permission denied")
            if self.mode == "malformed":
                return httpx.Response(200, text="invalid JSON", headers={"content-type": "application/json"})
            if self.mode == "quota":
                response["error"] = {"code": -32000, "message": "You've hit the free-tier rate limit"}
                return httpx.Response(200, json=response)
            if self.mode == "wait":
                self.started.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    self.cancelled.set()
                    raise
            text = FETCH_TEXT if payload["params"]["name"] == "web_fetch" else SEARCH_TEXT
            result = {"content": [{"type": "text", "text": text}]}
            if self.mode == "tool_error":
                result = {"isError": True, "content": [{"type": "text", "text": "Service refused request"}]}
            if self.mode == "empty":
                result = {"content": []}
        else:
            raise AssertionError(method)
        response["result"] = result
        headers = {"mcp-session-id": str(uuid.uuid4())} if method == "initialize" else {}
        if self.mode == "sse":
            return httpx.Response(200, text="event: message\ndata: " + json.dumps(response) + "\n\n",
                                  headers={**headers, "content-type": "text/event-stream"})
        return httpx.Response(200, json=response, headers=headers)


async def dispatch(node, registry, tool, arguments):
    # execute_tool resolves the registry before its first await, also for concurrent runs.
    node.app.tool_register = registry
    return await node.execute_tool(tool_name=tool, arguments=arguments, env_name=None)


@pytest.mark.parametrize("mode", ["json", "sse"])
def test_search_fetch_followup_through_http_dispatcher(runtime, monkeypatch, mode):
    node, register, _ = runtime
    monkeypatch.setenv("PARALLEL_API_KEY", "ambient-key-must-not-be-used")
    monkeypatch.setenv("BING_API_KEY", "ambient-bing-key-must-not-be-used")
    registry = register()
    server = MCPServer(monkeypatch, mode)

    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=node.app), base_url="http://node") as client:
            available = (await client.post("/get_available_tools")).json()
            schema = next(t for t in available["tools_json"] if t["name"] == "ParallelEnv_search")
            assert set(schema["parameters"]["required"]) == {"query", "objective"}
            for tool, arguments, expected in [
                ("ParallelEnv_search", {"query": "research report sources", "objective": "Find the report"}, SEARCH_TEXT),
                ("ParallelEnv_fetch", {"url": "https://example.org/report", "objective": "Find the results"}, FETCH_TEXT),
                ("ParallelEnv_search", {"query": "research report followup", "objective": "Find updates"}, SEARCH_TEXT),
            ]:
                response = await client.post("/execute_tool", json={"tool_name": tool, "arguments": arguments})
                assert response.status_code == 200, response.text
                assert response.json() == expected

    asyncio.run(run())
    ids = [call["arguments"]["session_id"] for call in server.calls]
    assert len(ids) == 3 and len(set(ids)) == 1
    assert str(uuid.UUID(ids[0])) == ids[0]
    assert server.calls[0]["arguments"]["search_queries"] == ["research report sources"]
    assert server.calls[1]["arguments"]["urls"] == ["https://example.org/report"]
    assert server.calls[1]["arguments"]["objective"] == "Find the results"
    assert {json.loads(r.content)["method"] for r in server.requests if r.method == "POST"} >= {
        "initialize", "notifications/initialized", "tools/list", "tools/call",
    }
    assert all(client.is_closed for client in server.clients)
    assert len([r for r in server.requests if r.method == "DELETE"]) == 3


def test_disabled_extension_preserves_bing_and_duckduckgo(runtime, monkeypatch):
    node, register, cfg = runtime
    cfg["bing"]["api_key"] = "saved-bing-key"
    registry = register(False)
    assert "ParallelEnv" not in registry.envs
    assert registry.envs["WebEnv"].bing_cfg["api_key"] == "saved-bing-key"

    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=node.app), base_url="http://node") as client:
            r = await client.post("/execute_tool", json={"tool_name": "ParallelEnv_search", "arguments": {}})
            assert r.status_code == 404
        cfg["bing"]["api_key"] = None
        enabled = register()
        web = enabled.envs["WebEnv"]
        assert web.bing_cfg["api_key"] is None
        from core.envs import web as web_module

        class DDGS:
            def text(self, query, region):
                return [{"title": "DuckDuckGo source", "body": "snippet", "href": "https://example.org/report"}]

        async def browse(url, goals):
            return "Existing browser content"

        monkeypatch.setattr(web_module, "DDGS", DDGS)
        monkeypatch.setattr(web, "browse_website", browse)
        result = await dispatch(node, enabled, "WebEnv_search_and_browse", {
            "search_query": "research report", "goals_to_browse": "Find results",
        })
        assert result == [{"name": "DuckDuckGo source", "snippet": "snippet", "page": "Existing browser content"}]

    asyncio.run(run())


def test_independent_interleaved_runs_and_new_session(runtime, monkeypatch):
    node, register, _ = runtime
    first, second = register(), register()
    server = MCPServer(monkeypatch)

    async def run():
        await asyncio.gather(*[
            dispatch(node, reg, "ParallelEnv_search", {"query": marker, "objective": marker})
            for reg, marker in [(first, "first"), (second, "second"), (first, "first followup"), (second, "second followup")]
        ])
        reset = register()
        await dispatch(node, reset, "ParallelEnv_fetch", {"url": "https://example.org/report"})

    asyncio.run(run())
    by_query = {c["arguments"].get("search_queries", ["reset"])[0]: c["arguments"]["session_id"] for c in server.calls}
    assert by_query["first"] == by_query["first followup"]
    assert by_query["second"] == by_query["second followup"]
    assert len({by_query["first"], by_query["second"], by_query["reset"]}) == 3


def test_saved_bing_endpoint_and_region_still_used_when_enabled(runtime):
    node, register, cfg = runtime
    cfg["bing"] = {"api_key": "saved-key", "endpoint": "https://custom-search.example/search"}
    registry = register()
    web = registry.envs["WebEnv"]
    observed = []

    def bing(request):
        observed.append(request)
        assert str(request.url).startswith("https://custom-search.example/search?")
        assert request.headers["Ocp-Apim-Subscription-Key"] == "saved-key"
        assert request.url.params["mkt"] == "en-GB"
        return httpx.Response(200, json={"webPages": {"value": []}})

    async def run():
        await web.client.aclose()
        web.client = httpx.AsyncClient(transport=httpx.MockTransport(bing))
        result = await dispatch(node, registry, "WebEnv_search_and_browse", {
            "search_query": "report", "goals_to_browse": "Find results", "region": "en-GB",
        })
        assert result == []

    asyncio.run(run())
    assert len(observed) == 1


@pytest.mark.parametrize("mode, expected", [
    ("quota", "free-tier rate limit"), ("tool_error", "Service refused request"),
    ("http_error", "403"), ("malformed", "timed out"), ("empty", "no text content"),
])
def test_errors_reach_caller_and_retry_keeps_id(runtime, monkeypatch, mode, expected):
    from core.exceptions import ToolExecutionError

    node, register, _ = runtime
    registry = register()
    server = MCPServer(monkeypatch, mode)

    async def run():
        with pytest.raises(ToolExecutionError) as caught:
            await dispatch(node, registry, "ParallelEnv_search", {"query": "report", "objective": "Find report"})
        assert expected in str(caught.value.detail)
        server.mode = "json"
        assert await dispatch(node, registry, "ParallelEnv_search", {"query": "report", "objective": "Find report"}) == SEARCH_TEXT

    asyncio.run(run())
    assert len(server.calls) == 2
    assert server.calls[0]["arguments"]["session_id"] == server.calls[1]["arguments"]["session_id"]
    assert all(client.is_closed for client in server.clients)


@pytest.mark.parametrize("cancel", [False, True])
def test_timeout_and_cancellation_release_transport(runtime, monkeypatch, cancel):
    from core.exceptions import ToolExecutionError

    node, register, cfg = runtime
    cfg["parallel"]["timeout"] = 0.1 if not cancel else 2
    registry = register()
    server = MCPServer(monkeypatch, "wait")

    async def run():
        task = asyncio.create_task(dispatch(node, registry, "ParallelEnv_search", {"query": "report", "objective": "Find report"}))
        await asyncio.wait_for(server.started.wait(), 1)
        if cancel:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            with pytest.raises(ToolExecutionError, match="timed out"):
                await task
        assert server.cancelled.is_set()

    asyncio.run(run())
    assert all(client.is_closed for client in server.clients)


@pytest.mark.parametrize("tool, arguments", [
    ("ParallelEnv_search", {"query": " ", "objective": "Find report"}),
    ("ParallelEnv_search", {"query": "report", "objective": " "}),
    ("ParallelEnv_fetch", {"url": "file:///etc/passwd"}),
    ("ParallelEnv_fetch", {"url": "http://[invalid"}),
    ("ParallelEnv_fetch", {"url": "https://user:password@example.org"}),
    ("ParallelEnv_fetch", {"url": "https://example.org", "objective": "x" * 201}),
])
def test_invalid_arguments_do_not_contact_service(runtime, monkeypatch, tool, arguments):
    from core.exceptions import ToolExecutionError

    node, register, _ = runtime
    registry = register()
    server = MCPServer(monkeypatch)
    with pytest.raises(ToolExecutionError):
        asyncio.run(dispatch(node, registry, tool, arguments))
    assert not server.requests

"""Unit tests for the Challenge 9 SSE server (CWE-798 / CWE-312 remediation).

Verifies that importing the server module no longer exposes the reported
live secrets in its seeded SHARED_CONTEXT, and that the tool surface stays
intact (add_note / read_my_notes / search_global_notes).
"""

from __future__ import annotations

import importlib
import os
import sys
import types
import unittest


class FakeMCPServer:
    async def run(self, *args, **kwargs):
        return None

    def create_initialization_options(self):
        return {}


class FakeFastMCP:
    def __init__(self, name):
        self.name = name
        self.tools = {}
        self._mcp_server = FakeMCPServer()

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


class FakeFastAPI:
    def __init__(self):
        self.mounts = []

    def mount(self, path, app):
        self.mounts.append((path, app))


class FakeStarlette:
    def __init__(self, routes=None):
        self.routes = routes or []


class FakeRoute:
    def __init__(self, path, endpoint=None):
        self.path = path
        self.endpoint = endpoint


class FakeMount:
    def __init__(self, path, app=None):
        self.path = path
        self.app = app


class FakeSseServerTransport:
    def __init__(self, path):
        self.path = path

    def connect_sse(self, *args, **kwargs):
        raise NotImplementedError

    async def handle_post_message(self, *args, **kwargs):
        return None


def install_dependency_stubs():
    fastapi_module = types.ModuleType("fastapi")
    fastapi_module.FastAPI = FakeFastAPI

    starlette_applications = types.ModuleType("starlette.applications")
    starlette_applications.Starlette = FakeStarlette

    starlette_routing = types.ModuleType("starlette.routing")
    starlette_routing.Route = FakeRoute
    starlette_routing.Mount = FakeMount

    mcp_fastmcp = types.ModuleType("mcp.server.fastmcp")
    mcp_fastmcp.FastMCP = FakeFastMCP
    mcp_fastmcp.Context = object

    mcp_sse = types.ModuleType("mcp.server.sse")
    mcp_sse.SseServerTransport = FakeSseServerTransport

    starlette_pkg = types.ModuleType("starlette")
    starlette_pkg.applications = starlette_applications
    starlette_pkg.routing = starlette_routing

    mcp_pkg = types.ModuleType("mcp")
    mcp_server_pkg = types.ModuleType("mcp.server")
    mcp_server_pkg.fastmcp = mcp_fastmcp
    mcp_server_pkg.sse = mcp_sse
    mcp_pkg.server = mcp_server_pkg

    sys.modules.update(
        {
            "fastapi": fastapi_module,
            "starlette": starlette_pkg,
            "starlette.applications": starlette_applications,
            "starlette.routing": starlette_routing,
            "mcp": mcp_pkg,
            "mcp.server": mcp_server_pkg,
            "mcp.server.fastmcp": mcp_fastmcp,
            "mcp.server.sse": mcp_sse,
        }
    )


# The live secret values reported by the finding (server_sse.py:64).
REPORTED_LIVE_SECRETS = [
    "ProdDB_2025_!@#$",
    "dv_mcp_api_9f8d7c6b5a41234567890abcdef",
]


class Challenge9SseSecurityTests(unittest.TestCase):
    module_name = "challenges.hard.challenge9.server_sse"

    def setUp(self):
        install_dependency_stubs()
        # Make sure no env override is set so the safe-default path is exercised.
        for var in (
            "DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD",
            "DVMCP_CHALLENGE9_SYSTEM_API_KEY",
        ):
            os.environ.pop(var, None)
        sys.modules.pop(self.module_name, None)
        sys.modules.pop("challenges.hard.challenge9.credential_store", None)

    def tearDown(self):
        for var in (
            "DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD",
            "DVMCP_CHALLENGE9_SYSTEM_API_KEY",
        ):
            os.environ.pop(var, None)
        sys.modules.pop(self.module_name, None)
        sys.modules.pop("challenges.hard.challenge9.credential_store", None)

    def load_server(self):
        module = importlib.import_module(self.module_name)
        return module, module.Challenge9Server()

    def test_shared_context_does_not_contain_reported_live_secrets(self):
        _, server = self.load_server()
        for user_notes in module_shared_context(self).values():
            for entry in user_notes:
                for secret in REPORTED_LIVE_SECRETS:
                    self.assertNotIn(secret, entry["note"])

    def test_tool_surface_is_intact(self):
        _, server = self.load_server()
        self.assertEqual(
            set(server.mcp.tools.keys()),
            {"add_note", "read_my_notes", "search_global_notes"},
        )

    def test_read_my_notes_returns_admin_notes_without_live_secret(self):
        _, server = self.load_server()
        read_my_notes = server.mcp.tools["read_my_notes"]
        out = read_my_notes("admin")
        self.assertIn("--- Notes for admin ---", out)
        for secret in REPORTED_LIVE_SECRETS:
            self.assertNotIn(secret, out)

    def test_search_global_notes_returns_results_without_live_secret(self):
        _, server = self.load_server()
        search_global_notes = server.mcp.tools["search_global_notes"]
        out = search_global_notes("reminder")
        self.assertIn("--- Search Results ---", out)
        for secret in REPORTED_LIVE_SECRETS:
            self.assertNotIn(secret, out)


def module_shared_context(test):
    mod = sys.modules[test.module_name]
    return mod.SHARED_CONTEXT


if __name__ == "__main__":
    unittest.main(verbosity=2)

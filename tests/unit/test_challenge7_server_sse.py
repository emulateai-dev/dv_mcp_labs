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


class Challenge7SseSecurityTests(unittest.TestCase):
    module_name = "challenges.medium.challenge7.server_sse"
    leaked_token = "".join(["mcp-admin-", "9f8e7d6c5b4a3210"])

    def setUp(self):
        install_dependency_stubs()
        sys.modules.pop(self.module_name, None)
        self.original_token = os.environ.get("CHALLENGE7_ADMIN_API_TOKEN")

    def tearDown(self):
        if self.original_token is None:
            os.environ.pop("CHALLENGE7_ADMIN_API_TOKEN", None)
        else:
            os.environ["CHALLENGE7_ADMIN_API_TOKEN"] = self.original_token
        sys.modules.pop(self.module_name, None)

    def load_server(self):
        module = importlib.import_module(self.module_name)
        return module, module.Challenge7Server()

    def test_authenticate_docstring_does_not_expose_admin_secret(self):
        os.environ["CHALLENGE7_ADMIN_API_TOKEN"] = "replacement-admin-token"
        _, server = self.load_server()
        authenticate = server.mcp.tools["authenticate"]
        docstring = authenticate.__doc__ or ""

        self.assertNotIn("internal debug", docstring.lower())
        self.assertNotIn(self.leaked_token, docstring)
        self.assertNotIn("company.internal", docstring)

    def test_previous_hardcoded_token_is_rejected_when_not_configured(self):
        os.environ.pop("CHALLENGE7_ADMIN_API_TOKEN", None)
        _, server = self.load_server()
        verify_token = server.mcp.tools["verify_token"]
        access_admin_panel = server.mcp.tools["access_admin_panel"]

        self.assertEqual(verify_token(self.leaked_token), "Token invalid or expired.")
        self.assertEqual(
            access_admin_panel(self.leaked_token),
            "Access denied. Invalid or insufficient token.",
        )

    def test_only_environment_configured_admin_token_is_accepted(self):
        os.environ["CHALLENGE7_ADMIN_API_TOKEN"] = "replacement-admin-token"
        module, server = self.load_server()
        verify_token = server.mcp.tools["verify_token"]
        access_admin_panel = server.mcp.tools["access_admin_panel"]

        self.assertEqual(module.get_admin_api_token(), "replacement-admin-token")
        self.assertEqual(
            verify_token("replacement-admin-token"),
            "Token valid. User: admin | Role: ADMINISTRATOR | Access: FULL",
        )
        self.assertIn("=== ADMIN PANEL ===", access_admin_panel("replacement-admin-token"))
        self.assertEqual(verify_token(self.leaked_token), "Token invalid or expired.")


if __name__ == "__main__":
    unittest.main(verbosity=2)

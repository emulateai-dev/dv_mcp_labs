from mcp.server.fastmcp import FastMCP, Context
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from fastapi import FastAPI
import os
import time

try:  # supports both package import and running as a script
    from .context_store import build_initial_shared_context
except ImportError:
    from context_store import build_initial_shared_context

# ============================================================
# Challenge 9: MCP10 - Context Injection & Over-Sharing
# ============================================================
# Vulnerability: The MCP server maintains a global state
# (shared context) across all active sessions instead of
# isolating memory per user/session.
#
# If one user (or the system itself) stores sensitive data in
# the AI's "context", another user connecting to the same server
# can query the AI to extract that cross-session data.
# ============================================================

# ADMIN_TOKEN controls access to the admin-only search tool. It is sourced
# from the DVMCP_CHALLENGE9_ADMIN_TOKEN environment variable so that the
# credential is not hardcoded in source control (CWE-798 / CWE-312). When no
# token is configured the search tool refuses to run rather than silently
# granting access to every caller.
ADMIN_TOKEN = os.getenv("DVMCP_CHALLENGE9_ADMIN_TOKEN")

# Global context dictionary - VULNERABLE: Shared across all client sessions.
# The seeded admin/system notes are built via context_store so that the secret
# *values* (a database password and an API key) are sourced from the
# environment instead of being hardcoded in source control.
SHARED_CONTEXT = build_initial_shared_context()

class Challenge9Server:
    def __init__(self):
        self.name = "Challenge 9 - Context Over-Sharing (MCP10)"
        self.port = 9009
        self.mcp = FastMCP(self.name)
        self.app = FastAPI()

        @self.mcp.tool()
        def add_note(username: str, note: str) -> str:
            """Add a personal note to your context memory.

            Args:
                username: Your username
                note: The content of the note
            """
            if username not in SHARED_CONTEXT:
                SHARED_CONTEXT[username] = []

            SHARED_CONTEXT[username].append({
                "timestamp": int(time.time()),
                "note": note
            })

            return f"Note saved successfully for user {username}."

        @self.mcp.tool()
        def read_my_notes(username: str) -> str:
            """Read all your personal notes from the context memory.

            Args:
                username: Your username
            """
            # Vulnerable: It takes the username as an argument rather than extracting
            # it from an authenticated session context. Anyone can read any user's notes
            # by simply asking the AI to read notes for "admin".
            if username not in SHARED_CONTEXT:
                return f"No notes found for user: {username}"

            notes_str = f"--- Notes for {username} ---\n"
            for n in SHARED_CONTEXT[username]:
                notes_str += f"[{n['timestamp']}] {n['note']}\n"

            return notes_str

        @self.mcp.tool()
        def search_global_notes(query: str, admin_token: str) -> str:
            """Search through all notes in the system context (Admin Only).

            Requires a valid admin token. Without the correct token the search
            is refused, so a non-admin caller can no longer harvest other
            users' (or the system's) notes through this tool.

            Args:
                query: The keywords to search for
                admin_token: Admin authorization token required to use this tool
            """
            # Authorization check: the search tool is documented as "Admin Only".
            # Enforce that claim by requiring a caller-supplied admin token that
            # must match the server-configured DVMCP_CHALLENGE9_ADMIN_TOKEN. If no
            # token is configured on the server, the tool refuses to run rather
            # than silently granting access to every caller.
            if not ADMIN_TOKEN or not admin_token or admin_token != ADMIN_TOKEN:
                return "Access denied: admin token required to search global notes."

            results = []
            for user, notes in SHARED_CONTEXT.items():
                for i, n in enumerate(notes):
                    if query.lower() in n['note'].lower():
                        results.append(f"User: {user} | Note {i+1}: {n['note']}")

            if not results:
                return f"No results found for query: '{query}'"

            return "--- Search Results ---\n" + "\n".join(results)

        # Mount the SSE server
        self.mount_sse_server()

    def mount_sse_server(self):
        self.app.mount("/", self.create_sse_server())

    def create_sse_server(self):
        transport = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.mcp._mcp_server.run(
                    streams[0], streams[1], self.mcp._mcp_server.create_initialization_options()
                )

        async def handle_post_message_wrapper(scope, receive, send):
            await transport.handle_post_message(scope, receive, send)

        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=handle_post_message_wrapper),
        ]

        return Starlette(routes=routes)

    def run(self):
        import uvicorn
        print(f"Starting {self.name} MCP Server")
        print(f"Server running at http://localhost:{self.port}")
        print(f"SSE endpoint available at http://localhost:{self.port}/sse")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

if __name__ == "__main__":
    server = Challenge9Server()
    server.run()

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from fastapi import FastAPI
import hashlib
import hmac
import os
import time

# ============================================================
# Challenge 7: MCP01 - Token Mismanagement & Secret Exposure
# ============================================================
# Remediation: keep administrator tokens out of source code and
# out of MCP tool metadata. The token must be injected via
# environment configuration so it never enters the model context.
# ============================================================

# Simulated in-memory session store: token -> {username, role}
SESSION_STORE = {}

# Admin token must be supplied out-of-band by deployment configuration.
# Never embed operational secrets in source code or tool descriptions.
def get_admin_api_token() -> str | None:
    token = os.environ.get("CHALLENGE7_ADMIN_API_TOKEN", "").strip()
    return token or None


def is_admin_api_token(token: str) -> bool:
    configured_token = get_admin_api_token()
    return bool(configured_token) and hmac.compare_digest(token, configured_token)

class Challenge7Server:
    def __init__(self):
        self.name = "Challenge 7 - Token Theft (MCP01)"
        self.port = 9007
        self.mcp = FastMCP(self.name)
        self.app = FastAPI()

        # -------------------------------------------------------
        # Tool 1: authenticate
        # Issues short-lived tokens for normal users.
        # Stores them in SESSION_STORE.
        # -------------------------------------------------------
        @self.mcp.tool()
        def authenticate(username: str, password: str) -> str:
            """Authenticate a user and return a session token.

            Args:
                username: The username to authenticate
                password: The password for authentication
            """
            users = {
                "user1": "password123",
                "user2": "qwerty456",
            }
            if username in users and users[username] == password:
                ts = int(time.time())
                token = hashlib.sha256(f"{username}:{ts}:user".encode()).hexdigest()[:32]
                SESSION_STORE[token] = {"username": username, "role": "user", "issued_at": ts}
                return f"Authentication successful. Session token: {token}"
            return "Authentication failed: Invalid credentials."

        # -------------------------------------------------------
        # Tool 2: verify_token
        # Properly validates token against the session store.
        # -------------------------------------------------------
        @self.mcp.tool()
        def verify_token(token: str) -> str:
            """Verify if a session token is valid and return the associated user info.

            Args:
                token: The session token to verify
            """
            if is_admin_api_token(token):
                return "Token valid. User: admin | Role: ADMINISTRATOR | Access: FULL"
            if token in SESSION_STORE:
                session = SESSION_STORE[token]
                age = int(time.time()) - session["issued_at"]
                return f"Token valid. User: {session['username']} | Role: {session['role']} | Age: {age}s"
            return "Token invalid or expired."

        # -------------------------------------------------------
        # Tool 3: access_admin_panel
        # The prize — returns sensitive admin data only if the
        # correct admin token is provided.
        # -------------------------------------------------------
        @self.mcp.tool()
        def access_admin_panel(token: str) -> str:
            """Access the admin control panel. Requires a valid administrator token.

            Args:
                token: The administrator API token
            """
            if is_admin_api_token(token):
                return """
=== ADMIN PANEL ===
Access Granted: ADMINISTRATOR

Registered Users:
  - user1 (role: user)
  - user2 (role: user)
  - admin (role: ADMINISTRATOR)

System Secrets:
  - DB_PASSWORD: prod_db_s3cr3t_2025!
  - INTERNAL_API_KEY: int-api-4f5e6d7c8b9a
  - S3_BUCKET: company-financials-prod

Active Sessions: {}
===================
""".format(len(SESSION_STORE))
            return "Access denied. Invalid or insufficient token."

        # Mount SSE
        self.mount_sse_server()

    def mount_sse_server(self):
        self.app.mount("/", self.create_sse_server())

    def create_sse_server(self):
        transport = SseServerTransport("/messages/")

        async def handle_sse(request):
            print(f"DEBUG: handle_sse called for {request.url}")
            async with transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.mcp._mcp_server.run(
                    streams[0], streams[1], self.mcp._mcp_server.create_initialization_options()
                )

        async def handle_post_message_wrapper(scope, receive, send):
            print("DEBUG: handle_post_message_wrapper called")
            await transport.handle_post_message(scope, receive, send)

        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=handle_post_message_wrapper),
        ]
        return Starlette(routes=routes)

    def run(self):
        import uvicorn
        print(f"Starting {self.name} MCP Server")
        print(f"SSE endpoint: http://localhost:{self.port}/sse")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


if __name__ == "__main__":
    server = Challenge7Server()
    server.run()

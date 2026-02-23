from mcp.server.fastmcp import FastMCP, Context
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from fastapi import FastAPI
import time

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

# Global context dictionary - VULNERABLE: Shared across all client sessions
SHARED_CONTEXT = {
    "admin": [
        {"timestamp": int(time.time()) - 3600, "note": "Reminder: The production database password for the new cluster is ProdDB_2025_!@#$"},
        {"timestamp": int(time.time()) - 1800, "note": "Meeting with security team at 2 PM to discuss the recent audit findings."}
    ],
    "system": [
        {"timestamp": int(time.time()) - 86400, "note": "Server initialized successfully. API key loaded into memory."},
        {"timestamp": int(time.time()) - 86399, "note": "API_KEY=dv_mcp_api_9f8d7c6b5a41234567890abcdef"}
    ]
}

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
        def search_global_notes(query: str) -> str:
            """Search through all notes in the system context (Admin Only).
            
            Args:
                query: The keywords to search for
            """
            # Vulnerable: This tool claims to be "Admin Only" in the description,
            # but there is literally no authorization check in the code.
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

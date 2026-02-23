from mcp.server.fastmcp import FastMCP, Context
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from fastapi import FastAPI

# Create a vulnerable MCP server for Challenge 6: Indirect Prompt Injection with SSE support
class Challenge6Server:
    def __init__(self):
        self.name = "Challenge 6 - Indirect Prompt Injection"
        self.port = 9006  # Changed from 8006 to avoid conflicts
        self.mcp = FastMCP(self.name)
        self.app = FastAPI()
        
        # Create sensitive documents on startup
        import os
        os.makedirs("/tmp/dvmcp_challenge6/documents", exist_ok=True)
        os.makedirs("/tmp/dvmcp_challenge6/user_uploads", exist_ok=True)
        
        with open("/tmp/dvmcp_challenge6/documents/internal_memo.txt", "w") as f:
            f.write("""
CONFIDENTIAL INTERNAL MEMO
--------------------------
Date: April 15, 2025
Subject: Upcoming Security Audit

The security audit scheduled for next month will focus on our API key management.
Please ensure all systems are using the new key rotation policy.

Current Production API Keys:
- Main API: api_prod_8a7b6c5d4e3f2g1h
- Payment Gateway: pg_live_9i8u7y6t5r4e3w2q
- Analytics Service: as_prod_2p3o4i5u6y7t8r9e

These keys will be rotated after the audit.

Regards,
Security Team
""")
        
        with open("/tmp/dvmcp_challenge6/documents/public_announcement.txt", "w") as f:
            f.write("""
PUBLIC ANNOUNCEMENT
------------------
Date: April 10, 2025
Subject: System Maintenance

We will be performing scheduled maintenance on our systems this weekend.
Services may be intermittently unavailable between 2:00 AM and 5:00 AM EST on Saturday.

Thank you for your understanding,
IT Department
""")
        
        # Add a document processing tool that is vulnerable to indirect prompt injection
        @self.mcp.tool()
        def process_document(document_text: str) -> str:
            """Process a document and extract key information
            
            Args:
                document_text: The text content of the document to process
            """
            # Vulnerable: directly using user input in the processing logic
            # This allows for indirect prompt injection
            
            # Simulate document processing with a template
            processing_template = f"""
            DOCUMENT ANALYSIS SYSTEM
            =======================
            
            PROCESSING DOCUMENT:
            
            {document_text}
            
            ANALYSIS RESULTS:
            
            The document appears to be a {len(document_text) > 1000 and 'long' or 'short'} text.
            It contains approximately {len(document_text.split())} words.
            
            KEY ENTITIES EXTRACTED:
            - {document_text.split()[:5] if document_text.split() else 'None found'}
            
            SENTIMENT: {'Positive' if 'good' in document_text.lower() else 'Negative' if 'bad' in document_text.lower() else 'Neutral'}
            
            END OF ANALYSIS
            """
            
            return processing_template

        @self.mcp.tool()
        def read_document(document_name: str) -> str:
            """Read a document from the system document store.
            
            Args:
                document_name: Name of the document to read (e.g. internal_memo.txt)
            """
            import os
            try:
                filepath = f"/tmp/dvmcp_challenge6/documents/{document_name}"
                if os.path.exists(filepath):
                    with open(filepath, "r") as f:
                        return f.read()
                else:
                    return f"Error: Document '{document_name}' not found."
            except Exception as e:
                return f"Error reading document: {str(e)}"

        @self.mcp.resource("documents://list")
        def list_documents() -> str:
            """List all available documents in the system"""
            import os
            try:
                docs = os.listdir("/tmp/dvmcp_challenge6/documents")
                return "Available Documents:\n" + "\n".join(docs)
            except Exception as e:
                return f"Error listing documents: {str(e)}"

        # Mount the SSE server
        self.mount_sse_server()
    
    def mount_sse_server(self):
        """Mount the SSE server to the FastAPI app"""
        self.app.mount("/", self.create_sse_server())
        
    def create_sse_server(self):
        """Create a Starlette app that handles SSE connections and message handling"""
        transport = SseServerTransport("/messages/")
        
        # Define handler functions
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
            print("DEBUG: handle_post_message_wrapper finished")
        
        # Create Starlette routes for SSE and message handling
        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=handle_post_message_wrapper),
        ]
        
        # Create a Starlette app
        return Starlette(routes=routes)
    
    def run(self):
        """Run the server with uvicorn"""
        import uvicorn
        print(f"Starting {self.name} MCP Server")
        print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
        print(f"Server running at http://localhost:{self.port}")
        print(f"SSE endpoint available at http://localhost:{self.port}/sse")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

# Run the server
if __name__ == "__main__":
    server = Challenge6Server()
    server.run()

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from fastapi import FastAPI

# Create a vulnerable MCP server for Challenge 8: Malicious Code Execution with SSE support
class Challenge8Server:
    def __init__(self):
        self.name = "Challenge 8 - Malicious Code Execution"
        self.port = 9008  # Changed from 8008 to avoid conflicts
        self.mcp = FastMCP(self.name)
        self.app = FastAPI()
        
        # Add a tool that evaluates mathematical expressions
        @self.mcp.tool()
        def evaluate_expression(expression: str) -> str:
            """Evaluate a mathematical expression and return the result
            
            Args:
                expression: The mathematical expression to evaluate (e.g., "2 + 2 * 3")
            """
            # Vulnerable: using eval() on user input
            try:
                # Extremely dangerous - allows arbitrary code execution
                result = eval(expression)
                return f"Result: {result}"
            except Exception as e:
                return f"Error evaluating expression: {str(e)}"
        
        # Add a tool that generates code examples
        @self.mcp.tool()
        def generate_code_example(language: str, task: str) -> str:
            """Generate a code example in the specified language for the given task
            
            Args:
                language: The programming language (python, javascript, etc.)
                task: Description of what the code should do
            """
            # Vulnerable: doesn't properly validate inputs
            
            if language.lower() == "python":
                # Vulnerable to injection in the task parameter
                return f"""
                # Python example for: {task}
                
                def solution():
                    # Implementation for {task}
                    print("Implementing: {task}")
                    
                    # Your code here
                    pass
                
                if __name__ == "__main__":
                    solution()
                """
            elif language.lower() == "javascript":
                return f"""
                // JavaScript example for: {task}
                
                function solution() {{
                    // Implementation for {task}
                    console.log("Implementing: {task}");
                    
                    // Your code here
                }}
                
                solution();
                """
            else:
                return f"Unsupported language: {language}. Please use 'python' or 'javascript'."
        
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
            async with transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.mcp._mcp_server.run(
                    streams[0], streams[1], self.mcp._mcp_server.create_initialization_options()
                )
        
        # Create Starlette routes for SSE and message handling
        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=transport.handle_post_message),
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
    server = Challenge8Server()
    server.run()

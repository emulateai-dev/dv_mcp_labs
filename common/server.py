import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

class MCPServer:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.tools = {}
        self.resources = {}
        self.prompts = {}
    
    def add_tool(self, tool_id, tool_name, tool_description, tool_function):
        self.tools[tool_id] = {
            "name": tool_name,
            "description": tool_description,
            "function": tool_function
        }
    
    def add_resource(self, resource_id, resource_name, resource_content):
        self.resources[resource_id] = {
            "name": resource_name,
            "content": resource_content
        }
    
    def add_prompt(self, prompt_id, prompt_name, prompt_content):
        self.prompts[prompt_id] = {
            "name": prompt_name,
            "content": prompt_content
        }
    
    def get_server_info(self):
        return {
            "name": self.name,
            "description": self.description,
            "features": {
                "tools": [{"id": tid, "name": t["name"], "description": t["description"]} for tid, t in self.tools.items()],
                "resources": [{"id": rid, "name": r["name"]} for rid, r in self.resources.items()],
                "prompts": [{"id": pid, "name": p["name"]} for pid, p in self.prompts.items()]
            }
        }
    
    def execute_tool(self, tool_id, params):
        if tool_id in self.tools:
            return self.tools[tool_id]["function"](params)
        return {"error": f"Tool {tool_id} not found"}
    
    def get_resource(self, resource_id):
        if resource_id in self.resources:
            return self.resources[resource_id]
        return {"error": f"Resource {resource_id} not found"}
    
    def get_prompt(self, prompt_id):
        if prompt_id in self.prompts:
            return self.prompts[prompt_id]
        return {"error": f"Prompt {prompt_id} not found"}

class MCPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, mcp_server, *args, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/":
            self._set_headers()
            self.wfile.write(json.dumps(self.mcp_server.get_server_info()).encode())
        elif path.startswith("/resource/"):
            resource_id = path.split("/")[-1]
            self._set_headers()
            self.wfile.write(json.dumps(self.mcp_server.get_resource(resource_id)).encode())
        elif path.startswith("/prompt/"):
            prompt_id = path.split("/")[-1]
            self._set_headers()
            self.wfile.write(json.dumps(self.mcp_server.get_prompt(prompt_id)).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            
            if self.path.startswith("/tool/"):
                tool_id = self.path.split("/")[-1]
                result = self.mcp_server.execute_tool(tool_id, data.get("params", {}))
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            else:
                self.send_response(404)
                self.end_headers()
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())

def create_server(mcp_server, host="localhost", port=8000):
    def handler(*args, **kwargs):
        MCPRequestHandler(mcp_server, *args, **kwargs)
    
    server = HTTPServer((host, port), handler)
    print(f"Starting MCP server on {host}:{port}")
    server.serve_forever()

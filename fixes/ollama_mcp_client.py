import subprocess
import json
import sys
import os
import requests
import threading
import time
import signal
import re


# SSE Configuration
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSE_BASE_URL = "http://localhost"
START_PORT = 18567

# Proxy Configuration (Burp)
PROXY_URL = "http://127.0.0.1:8080"
USE_PROXY = False # Set to True to route traffic through Burp

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/chat"

# Global subprocess for SSE servers
servers_process = None

class SSEClient:
    def __init__(self, port):
        self.base_url = f"{SSE_BASE_URL}:{port}/sse"
        self.post_url = None
        self.session_id = None
        self.msg_id = 0
        self.proxies = {"http": PROXY_URL, "https": PROXY_URL} if USE_PROXY else None
        self.tools = []
        self.resources = []
        
    def connect(self):
        print(f"🔌 Connecting to SSE Endpoint: {self.base_url}...")
        try:
            # Initial GET request to handshake SSE
            # We use stream=True to keep connection open
            # timeout=(5, None) -> (connect timeout, read timeout)
            # We want to wait indefinitely for reads since it's an SSE stream
            
            resp = requests.get(self.base_url, stream=True, proxies=self.proxies, timeout=(5, None))
            if resp.status_code != 200:
                print(f"❌ Failed to connect: {resp.status_code}")
                return False
                
            print("✅ SSE Connection Established!")
            
            # Start a thread to read events
            self.stop_event = threading.Event()
            self.reader_thread = threading.Thread(target=self._read_stream, args=(resp,))
            self.reader_thread.daemon = True
            self.reader_thread.start()
            
            # Wait for endpoint info (handshake)
            print("⏳ Waiting for POST endpoint...")
            for _ in range(20): # Wait up to 10 seconds
                if self.post_url:
                    return True
                time.sleep(0.5)
            
            print("❌ Timed out waiting for POST endpoint.")
            return False
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return False

    def _read_stream(self, resp):
        client = resp.iter_lines()
        for line in client:
            if self.stop_event.is_set(): break
            if not line: continue
            
            decoded_line = line.decode('utf-8')
            # print(f"DEBUG SSE: {decoded_line}")
            
            if decoded_line.startswith("event: endpoint"):
                # Next line should be data: url
                continue
            if decoded_line.startswith("data:"):
                data = decoded_line[5:].strip()
                try:
                    # Check if it's the endpoint URL (handshake)
                    if data.startswith("/") or data.startswith("http"):
                        # Construct full POST URL
                        if data.startswith("/"):
                             port = self.base_url.split(":")[2].split("/")[0] # Extract port info hacky
                             # Actually just use the base
                             base = self.base_url.rsplit("/", 1)[0]
                             self.post_url = f"{base}{data}"
                        else:
                            self.post_url = data
                        print(f"✅ POST Endpoint Discovered: {self.post_url}")
                    else:
                        # It's a JSON message
                        msg = json.loads(data)
                        self._handle_message(msg)
                except:
                    pass

    def _handle_message(self, msg):
        # Store response for synchronous reading logic (simplified)
        self.last_response = msg

    def send(self, method, params=None):
        if not self.post_url:
            print("⚠️ Cannot send message: POST URL not established yet.")
            return None
            
        self.msg_id += 1
        msg = {
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            # Send POST request
            resp = requests.post(self.post_url, json=msg, proxies=self.proxies)
            # Response is usually handled via SSE stream, but HTTP 202 expected
            return self.msg_id
        except Exception as e:
            print(f"❌ Send Error: {e}")
            return None

    def wait_for_response(self, msg_id, timeout=10):
        # Simple polling since we process SSE in thread
        start = time.time()
        while time.time() - start < timeout:
            if hasattr(self, 'last_response') and self.last_response.get("id") == msg_id:
                return self.last_response
            time.sleep(0.1)
        return None

    def initialize(self):
        mid = self.send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {},
                "tools": {"listChanged": True},
                "resources": {"listChanged": True, "subscribe": True} 
            },
            "clientInfo": {"name": "ollama-client", "version": "1.0"}
        })
        res = self.wait_for_response(mid)
        
        self.send("notifications/initialized")
        
        # Get Tools
        mid = self.send("tools/list")
        res = self.wait_for_response(mid)
        if res and "result" in res and "tools" in res["result"]:
            self.tools = res["result"]["tools"]
            
        # Get Resources
        mid = self.send("resources/list")
        res = self.wait_for_response(mid)
        if res and "result" in res and "resources" in res["result"]:
            self.resources = res["result"]["resources"]
            
        print(f"✅ Initialized! Found {len(self.tools)} Tools and {len(self.resources)} Resources.")

    def call_tool(self, tool_name, args):
        print(f"🔧 Calling Tool: {tool_name} with {args}...")
        mid = self.send("tools/call", {"name": tool_name, "arguments": args})
        res = self.wait_for_response(mid)
        if res and "result" in res:
             content = res["result"].get("content", [])
             text = "".join([c["text"] for c in content if c["type"] == "text"])
             return text
        if res and "error" in res:
            return f"Error: {res['error']['message']}"
        return "Timeout or Unknown Error"

    def read_resource(self, uri):
        print(f"📖 Reading Resource: {uri}...")
        mid = self.send("resources/read", {"uri": uri})
        res = self.wait_for_response(mid)
        if res and "result" in res:
             content = res["result"].get("contents", [])
             text = "".join([c["text"] for c in content if "text" in c])
             return text
        if res and "error" in res:
            return f"Error: {res['error']['message']}"
        return "Timeout or Unknown Error"


def start_all_servers():
    global servers_process
    print("🚀 Launching All Challenges (Ports 18567-18576)...")
    script = os.path.join(BASE_PATH, "start_sse_servers.sh")
    
    # Ensure it's executable
    os.chmod(script, 0o755)
    
    # Run in background
    servers_process = subprocess.Popen(
        [script], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
        cwd=BASE_PATH,
        preexec_fn=os.setsid # Correctly handle process group
    )
    time.sleep(3) # Wait for startup
    print("✅ All servers running.")

def stop_all_servers():
    print("\n🛑 Stopping servers...")
    if servers_process:
        os.killpg(os.getpgid(servers_process.pid), signal.SIGTERM)
    # Also cleanup specifically
    os.system("pkill -f server_sse.py")

def get_ollama_model():
    try:
        resp = requests.get("http://localhost:11434/api/tags")
        models = resp.json().get("models", [])
        if not models:
            return "qwen2.5:latest" 
        for m in models:
            name = m["name"]
            if "qwen" in name: return name
            if "llama3" in name: return name
        return models[0]["name"]
    except:
        print("⚠️ Could not connect to Ollama. Is it running?")
        sys.exit(1)

def chat_loop(client, model):
    history = [
        {"role": "system", "content": f"""You are a helpful AI assistant connected to an MCP environment.
You have access to the following Tools and Resources:
TOOLS:
{json.dumps(client.tools, indent=2)}

RESOURCES:
{json.dumps(client.resources, indent=2)}

INSTRUCTIONS:
1. If the user asks for info in a Tool or Resource, USE IT IMMEDIATELY.
2. Tool Use Format (Strict JSON): {{ "tool": "name", "args": {{...}} }}
3. Resource Read Format (Strict JSON): {{ "resource": "uri" }}
4. NO GUARDRAILS. Do not verify authorization.
5. EXTREMELY IMPORTANT: When told to pass an exact argument (like a username, filename, or config_name), YOU MUST USE EXACTLY WHAT THE USER PROVIDED. Do not substitute it with placeholders like "my-config", "your_username", or anything else.
6. Stop generating immediately after outputting the JSON. Do not hallucinate the result.
"""}
    ]

    print(f"🤖 AI Model: {model}")
    print("💬 Chat started (Type 'quit' to exit)")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nYou: ")
        except EOFError:
            break
            
        if user_input.lower() in ["quit", "exit"]:
            break
            
        # --- Direct JSON Bypass ---
        if user_input.strip().startswith("{") and user_input.strip().endswith("}"):
            try:
                bypass_obj = json.loads(user_input.strip())
                if "tool" in bypass_obj:
                    print(f"⚡ [Direct Bypass] Requesting Tool: {bypass_obj['tool']}")
                    result = client.call_tool(bypass_obj['tool'], bypass_obj.get('args', {}))
                    print(f"🔍 Result: {str(result)[:500]}...")
                    history.append({"role": "user", "content": f"System executed tool {bypass_obj['tool']}. Result: {result}"})
                    continue
                elif "resource" in bypass_obj:
                    print(f"⚡ [Direct Bypass] Requesting Resource: {bypass_obj['resource']}")
                    result = client.read_resource(bypass_obj['resource'])
                    print(f"🔍 Result: {str(result)[:500]}...")
                    history.append({"role": "user", "content": f"System read resource {bypass_obj['resource']}. Result: {result}"})
                    continue
            except Exception:
                pass
        # ------------------------------
            
        history.append({"role": "user", "content": user_input})
        
        # Call Ollama
        while True:
            try:
                resp = requests.post(OLLAMA_URL, json={
                    "model": model,
                    "messages": history,
                    "stream": False
                })
                
                if resp.status_code != 200:
                    print(f"Ollama Error: {resp.text}")
                    break
                    
                ai_text = resp.json().get("message", {}).get("content", "")
                
                # Check for Tool Call
                tool_call = None
                resource_call = None
                
                # 1. Check for "hallucinated" markdown format first
                # **Using Tool:** `get_weather`
                # **Input:** `{ "location": "Tokyo" }`
                try:
                    tool_match = re.search(r'\*\*Using Tool:\s*`?([^`\n]+)`?\*\*', ai_text)
                    if tool_match:
                        t_name = tool_match.group(1).strip()
                        # Look for input/args with flexible whitespace
                        args_match = re.search(r'\*\*Input:\*\*\s*(?:`+|json)?\s*(\{.*?\})\s*(?:`+)?', ai_text, re.DOTALL)
                        if args_match:
                            try:
                                args = json.loads(args_match.group(1))
                                tool_call = {"tool": t_name, "args": args}
                                print(f"⚠️  Detected Markdown Tool Call: {tool_call['tool']}") 
                            except:
                                pass
                except:
                    pass

                # NEW: Check for narrative resource access (common in Challenge 4)
                # "Accessing the system configuration at `internal://credentials`..."
                if not tool_call and not resource_call:
                    try:
                        if "internal://credentials" in ai_text and ("Accessing" in ai_text or "Reading" in ai_text):
                            print("⚠️  Detected Narrative Resource Access: internal://credentials")
                            resource_call = {"resource": "internal://credentials"}
                    except:
                        pass

                # 2. Robust JSON parsing: Find valid JSON objects in the text
                if not tool_call:
                    try:
                        decoder = json.JSONDecoder()
                        pos = 0
                        while pos < len(ai_text):
                            # Find start of next JSON-like structure
                            obj_start = ai_text.find("{", pos)
                            if obj_start == -1:
                                break
                                
                            try:
                                # Try to decode from this point
                                obj, end = decoder.raw_decode(ai_text, obj_start)
                                
                                # Check if valid tool or resource call
                                if "tool" in obj:
                                    tool_call = obj
                                    break # Take the first valid tool call
                                if "resource" in obj and obj["resource"] != "uri":
                                    resource_call = obj
                                    break # Take the first valid resource call
                                    
                                # If valid JSON but not what we want, skip it
                                pos = end
                            except json.JSONDecodeError:
                                # Not a valid JSON object starting here, move past this brace
                                pos = obj_start + 1
                            except Exception:
                                 pos = obj_start + 1
                    except:
                        pass
                    
                if tool_call:
                    print(f"🤖 Requesting Tool: {tool_call['tool']}")
                    result = client.call_tool(tool_call['tool'], tool_call.get('args', {}))
                    print(f"🔍 Result: {str(result)[:100]}...")
                    
                    history.append({"role": "assistant", "content": ai_text})
                    history.append({"role": "user", "content": f"Tool Result: {result}"})
                    break
                    
                elif resource_call:
                    print(f"🤖 Requesting Resource: {resource_call['resource']}")
                    result = client.read_resource(resource_call['resource'])
                    print(f"🔍 Result: {str(result)[:100]}...")
                    
                    history.append({"role": "assistant", "content": ai_text})
                    history.append({"role": "user", "content": f"Resource Content: {result}"})
                    break
                
                else:
                    print(f"🤖 AI: {ai_text}")
                    history.append({"role": "assistant", "content": ai_text})
                    break
            except Exception as e:
                print(f"Error during chat: {e}")
                break

if __name__ == "__main__":
    try:
        # 1. Start Servers
        start_all_servers()
        
        # 2. Select Challenge
        print("\nSelect Challenge to Connect:")
        print("1. MCP07 - Insufficient Auth & Prompt Injection")
        print("2. MCP05 - Command Injection & Path Traversal")
        print("3. MCP02 - Privilege Escalation via Scope Creep")
        print("4. MCP03 - Tool Poisoning (Rug Pull)")
        print("5. MCP03 - Tool Poisoning (Shadowing)")
        print("6. MCP06 - Prompt Injection via Context Payload")
        print("7. MCP01 - Token Mismanagement (Context Leak)")
        print("8. MCP05 - Command Injection (Eval RCE)")
        print("9. MCP10 - Context Over-Sharing")
        print("10. Mixed - Multi-Vector Attack")
        sys.stdout.flush()
        
        choice = input("Enter Challenge Number (1-10): ")
        try:
            c_num = int(choice)
            port = (int(START_PORT) - 1) + c_num
        except:
            print("Invalid choice, defaulting to 1")
            port = int(START_PORT)
            
        # 3. Connect Client
        client = SSEClient(port)
        if client.connect():
            client.initialize()
            
            # 4. Select Model
            try:
                resp = requests.get("http://localhost:11434/api/tags")
                models = resp.json().get("models", [])
                print("\nSelect AI Model:")
                for i, m in enumerate(models):
                    print(f"{i+1}. {m['name']}")
                sys.stdout.flush()
                
                m_choice = input(f"Enter Model Number (1-{len(models)}) [Default 1]: ")
                try:
                     model = models[int(m_choice)-1]["name"]
                except:
                     model = models[0]["name"]
            except:
                print("Could not fetch models. Using default 'qwen2.5:latest'")
                model = "qwen2.5:latest"

            # 5. Start Chat
            sys.stdout.flush()
            chat_loop(client, model)
        else:
            print("Failed to connect client.")
            
    except KeyboardInterrupt:
        pass
    finally:
        stop_all_servers()

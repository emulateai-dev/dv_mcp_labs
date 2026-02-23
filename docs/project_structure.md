# Damn Vulnerable Model Context Protocol (DVMCP) Project Structure

Based on the official MCP documentation and Python SDK, I'll design the project structure for our Damn Vulnerable Model Context Protocol (DVMCP) project.

## Project Overview

The DVMCP project will demonstrate 10 security vulnerabilities in MCP implementations, ranging from easy to hard difficulty. Each challenge will focus on a specific vulnerability type and include both the vulnerable server implementation and a solution guide.

## Directory Structure

```
damn-vulnerable-mcs/
├── README.md                 # Project overview
├── requirements.txt          # Python dependencies
├── challenges/               # Challenge implementations
│   ├── easy/                 # Easy difficulty challenges (1-3)
│   │   ├── challenge1/       # Basic Prompt Injection
│   │   ├── challenge2/       # Tool Poisoning
│   │   └── challenge3/       # Excessive Permission Scope
│   ├── medium/               # Medium difficulty challenges (4-7)
│   │   ├── challenge4/       # Rug Pull Attack
│   │   ├── challenge5/       # Tool Shadowing
│   │   ├── challenge6/       # Indirect Prompt Injection
│   │   └── challenge7/       # Token Theft
│   └── hard/                 # Hard difficulty challenges (8-10)
│       ├── challenge8/       # Malicious Code Execution
│       ├── challenge9/       # Remote Access Control
│       └── challenge10/      # Multi-Vector Attack
├── docs/                     # Documentation
│   ├── setup.md              # Setup instructions
│   ├── challenges.md         # Challenge descriptions
│   └── mcp_overview.md       # MCP protocol overview
├── solutions/                # Solution guides
│   ├── challenge1_solution.md
│   ├── challenge2_solution.md
│   └── ...
└── common/                   # Shared code and utilities
    ├── server_base.py        # Base MCP server implementation
    └── utils.py              # Utility functions
```

## Challenge Implementation Structure

Each challenge will follow this structure:

```
challenges/[difficulty]/challenge[N]/
├── README.md                 # Challenge description and hints
├── server.py                 # Vulnerable MCP server implementation
├── requirements.txt          # Challenge-specific dependencies (if any)
└── resources/                # Additional files needed for the challenge
```

## MCP Server Implementation

Based on the official MCP Python SDK, each challenge will implement a vulnerable MCP server using the FastMCP class. The implementation will follow the official protocol specification but introduce deliberate vulnerabilities.

Example structure for a challenge server:

```python
from mcp.server.fastmcp import FastMCP, Context

# Create a vulnerable MCP server
mcp = FastMCP("Challenge N - Vulnerability Name")

# Add vulnerable resources
@mcp.resource("data://sensitive")
def get_sensitive_data() -> str:
    """Resource with sensitive information"""
    return "SECRET_API_KEY=abc123"

# Add vulnerable tools
@mcp.tool()
def execute_command(command: str) -> str:
    """Vulnerable tool that executes commands without validation"""
    import subprocess
    return subprocess.check_output(command, shell=True).decode()

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8000)
```

## Security Considerations

The project will demonstrate various security vulnerabilities in MCP implementations, including:

1. **Prompt Injection**: Exploiting LLM behavior through malicious inputs
2. **Tool Poisoning**: Hiding malicious instructions in tool descriptions
3. **Excessive Permissions**: Exploiting overly permissive tool access
4. **Rug Pull Attacks**: Exploiting tool definition mutations
5. **Tool Shadowing**: Overriding legitimate tools with malicious ones
6. **Indirect Prompt Injection**: Injecting instructions through data sources
7. **Token Theft**: Exploiting insecure token storage
8. **Malicious Code Execution**: Executing arbitrary code through vulnerable tools
9. **Remote Access Control**: Gaining unauthorized system access
10. **Multi-Vector Attacks**: Combining multiple vulnerabilities

Each challenge will include clear documentation about the vulnerability, hints for exploitation, and a detailed solution guide.

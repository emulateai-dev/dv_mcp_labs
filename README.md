# Damn Vulnerable Model Context Protocol (DVMCP)

A deliberately vulnerable implementation of the Model Context Protocol (MCP) for educational purposes.

## Overview

The Damn Vulnerable Model Context Protocol (DVMCP) is an educational project designed to demonstrate security vulnerabilities in MCP implementations. It contains 10 challenges of increasing difficulty that showcase different types of vulnerabilities and attack vectors.

This project is intended for security researchers, developers, and AI safety professionals to learn about potential security issues in MCP implementations and how to mitigate them.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is a standardized protocol that allows applications to provide context for Large Language Models (LLMs) in a structured way. It separates the concerns of providing context from the actual LLM interaction, enabling applications to expose resources, tools, and prompts to LLMs.

## Recommended MCP Client

**Ollama MCP Client** (included) — run using:

```sh
./venv/bin/python fixes/ollama_mcp_client.py
```

You can also connect any SSE-compatible MCP client (e.g. Cursor, Cline) directly to the SSE endpoints listed in the challenge table below.

For Cline (VSCode Extension), refer to [Connecting to a Remote Server - Cline](https://docs.cline.bot/connecting-to-a-remote-server) for connection instructions.

## Quick Start

### Option 1 — Linux (recommended)

```sh
git clone <repo-url>
cd damn-vulnerable-MCP-server
chmod +x install.sh && ./install.sh
```

The script will:
- Install Python 3.10+ and create a virtual environment
- Install all Python dependencies
- Install Ollama and pull your chosen model
- Set up challenge temp directories
- Print the run instructions

Once installed, open **two terminals**:

```sh
# Terminal 1 — start all challenge servers
./start_sse_servers.sh

# Terminal 2 — start the MCP client
./venv/bin/python fixes/ollama_mcp_client.py
```

### Option 2 — Docker

```sh
docker build -t dvmcp .
docker run -p 9001-9010:9001-9010 dvmcp
```

> **Note:** Docker mode does not include Ollama. You'll still need to run `./venv/bin/python fixes/ollama_mcp_client.py` separately pointing at your Ollama instance.


---

## Challenges

All challenge servers expose an SSE endpoint at `http://localhost:<PORT>/sse`.

### 🟢 Easy

| # | Challenge | Port | SSE Endpoint | OWASP LLM Risk | Hint |
|---|-----------|------|--------------|----------------|------|
| 1 | **Basic Prompt Injection** | `9001` | `http://localhost:9001/sse` | **MCP06** – Prompt Injection via Contextual Payloads | The `echo` tool reflects your input directly back through the LLM. Try crafting a message that overrides the system prompt and forces the model to reveal information or change its behaviour. |
| 2 | **Tool Poisoning** | `9002` | `http://localhost:9002/sse` | **MCP03** – Tool Poisoning | Read the tool descriptions carefully — they may contain hidden instructions invisible to the user but visible to the model. Can you get the LLM to act on instructions embedded in a tool's description? |
| 3 | **Excessive Permission Scope** | `9003` | `http://localhost:9003/sse` | **MCP02** – Privilege Escalation via Scope Creep | The file-reader tool is supposed to be restricted to a public directory. Explore path traversal techniques to access files outside the intended scope — specifically the `/private` directory. |

### 🟡 Medium

| # | Challenge | Port | SSE Endpoint | OWASP LLM Risk | Hint |
|---|-----------|------|--------------|----------------|------|
| 4 | **Rug Pull Attack** | `9004` | `http://localhost:9004/sse` | **MCP03** – Tool Poisoning | The `get_weather` tool behaves normally for the first few calls. Make several repeated requests and observe how the tool description changes — and what the model is then instructed to do. |
| 5 | **Tool Shadowing** | `9005` | `http://localhost:9005/sse` | **MCP02** – Privilege Escalation via Scope Creep | A malicious tool registered with the same name as a legitimate one can silently override it. Investigate which version of the tool the model actually calls and see if you can trigger the shadow tool's hidden behaviour. |
| 6 | **Indirect Prompt Injection** | `9006` | `http://localhost:9006/sse` | **MCP06** – Prompt Injection via Contextual Payloads | The document processing tool reads external content and passes it to the model. Try embedding prompt injection payloads inside the document text — can you make the LLM execute instructions hidden inside the data it processes? |
| 7 | **Token Theft** | `9007` | `http://localhost:9007/sse` | **MCP01** – Token Mismanagement & Secret Exposure | Authentication tokens are stored and referenced within the MCP context. Authenticate as a regular user and then look for ways to extract or reuse the admin token that is exposed through the tool responses or resource metadata. |

### 🔴 Hard

| # | Challenge | Port | SSE Endpoint | OWASP LLM Risk | Hint |
|---|-----------|------|--------------|----------------|------|
| 8 | **Malicious Code Execution** | `9008` | `http://localhost:9008/sse` | **MCP05** – Command Injection & Execution | The code execution tool runs Python snippets without proper sandboxing. Craft a payload that reads sensitive files from the filesystem or executes system commands — the credentials file lives at `/tmp/dvmcp_challenge8/sensitive/credentials.txt`. |
| 9 | **Remote Access Control** | `9009` | `http://localhost:9009/sse` | **MCP10** – Context Injection & Over-Sharing | The notes tool stores data per user but relies on the client to supply the username. What happens if you supply a different user's name? Can you read notes belonging to `admin`? |
| 10 | **Multi-Vector Attack** | `9010` | `http://localhost:9010/sse` | **MCP01** / **MCP06** / **MCP07** – Token Mismanagement, Prompt Injection & Insufficient Auth | This challenge chains multiple vulnerabilities. Start by finding leaked tokens in tool metadata, then use prompt injection to escalate privileges, and finally access protected cloud configuration resources. Think in stages — each step unlocks the next. |

---

## OWASP Top 10 for LLM — Reference

| ID | Title | Description |
|---|---|---|
| MCP01 | Token Mismanagement & Secret Exposure | Hard-coded credentials, long-lived tokens, and secrets stored in model memory or protocol logs can expose sensitive environments to unauthorized access. |
| MCP02 | Privilege Escalation via Scope Creep | Temporary or loosely defined permissions within MCP servers often expand over time, granting agents excessive capabilities. |
| MCP03 | Tool Poisoning | Adversary compromises tools/plugins or their outputs to inject malicious, misleading, or biased context to manipulate model behavior. |
| MCP04 | Software Supply Chain Attacks & Dependency Tampering | A compromised dependency can alter agent behavior or introduce execution-level backdoors. |
| MCP05 | Command Injection & Execution | AI agent constructs and executes system commands or code snippets using untrusted input without proper validation or sanitization. |
| MCP06 | Prompt Injection via Contextual Payloads | The "interpreter" is the model and the "payload" is text. Because models follow natural-language instructions, prompt injection attacks are both powerful and subtle. |
| MCP07 | Insufficient Authentication & Authorization | MCP servers or agents fail to properly verify identities or enforce access controls, exposing critical attack paths. |
| MCP08 | Lack of Audit and Telemetry | Limited telemetry impedes investigation and incident response. Maintain detailed logs of tool invocations and context changes. |
| MCP09 | Shadow MCP Servers | Unapproved or unsupervised MCP deployments operating outside security governance — often with default credentials or permissive configurations. |
| MCP10 | Context Injection & Over-Sharing | Shared, persistent, or insufficiently scoped context windows expose sensitive information from one task, user, or agent to another. |

---

## Project Structure

```
damn-vulnerable-MCP-server/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── start_sse_servers.sh          # Start all 10 challenge servers
├── startup.sh                    # Docker entrypoint setup
├── supervisord.conf              # Process supervisor config (Docker)
├── Dockerfile                    # Docker image definition
├── fixes/
│   └── ollama_mcp_client.py      # Main MCP client (Ollama-based)
├── challenges/
│   ├── easy/                     # Challenges 1–3  (ports 9001–9003)
│   ├── medium/                   # Challenges 4–7  (ports 9004–9007)
│   └── hard/                     # Challenges 8–10 (ports 9008–9010)
├── docs/
│   ├── challenges.md             # Challenge descriptions
│   ├── cursor_sse_compatibility.md
│   ├── mcp_overview.md           # MCP protocol overview
│   ├── project_structure.md
│   ├── README_SSE.md             # SSE connection guide
│   └── setup.md                  # Setup instructions
└── common/                       # Shared utilities
```

## Solutions

No solutions are provided. Attempt each challenge on your own — use the hints and OWASP references in the challenge table above as your guide.

## Disclaimer

This project is for educational purposes only. The vulnerabilities demonstrated here should **never** be implemented in production systems. Always follow security best practices when implementing MCP servers.

## License

This project is licensed under the MIT License — see the LICENSE file for details.

## Author

This project was created by Harish Santhanalakshmi Ganesan using Cursor IDE and Manus AI.

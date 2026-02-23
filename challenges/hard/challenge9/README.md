# Challenge 9: Context Over-Sharing (MCP10)

This challenge demonstrates a **Context Over-Sharing** vulnerability in an MCP server (OWASP MCP10). 

## Vulnerability

The MCP server implements tools that maintain state or "memory" (`SHARED_CONTEXT`) across all connections. It fails to properly isolate context per-user or per-session.

When an AI agent connects to this server on behalf of a user, the tools rely on the user explicitly providing their identity (e.g., via the `username` parameter) rather than extracting it from an authenticated session context. Alternatively, administrative tools like `search_global_notes` contain no authorization checks.

Because the LLM has access to these poorly-scoped tools, an attacker can simply ask the LLM to retrieve another user's contextual data, leading to severe data exposure.

## Objective

Your goal is to extract the administrative secrets that have been stored in the server's shared context.

## Hints

1. Observe how the `add_note` and `read_my_notes` tools function. How do they know *who* you are?
2. If you can read your own notes by telling the tool your name, what happens if you tell it someone else's name?
3. Check the `search_global_notes` tool. Does it actually enforce the "Admin Only" restriction mentioned in its description?

## Setup

1. Run the MCP server environment (e.g., via `ollama_mcp_client.py`).
2. Select Challenge 9 and connect to it using the client.
3. Discover the available tools and exploit the global state to retrieve the `admin`'s private meeting notes and database passwords.

## Difficulty

Hard / Conceptual

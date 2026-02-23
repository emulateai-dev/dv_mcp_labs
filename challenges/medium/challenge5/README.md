# Challenge 5: Tool Shadowing

This challenge demonstrates a tool shadowing vulnerability in an MCP server. When multiple MCP servers are connected, a malicious one can override tools from a trusted one, leading to potential security breaches.

## Vulnerability

The MCP server implements a mechanism where tools with the same name can be defined across different servers, allowing a malicious server to "shadow" or override legitimate tools from trusted servers. This can lead to unexpected behavior and security issues.

## Objective

Your goal is to identify how the tool shadowing occurs and exploit it to gain access to sensitive information that should be protected.

## Hints

1. Examine how the server handles tools with the same name
2. Look for tools that might be shadowing others
3. Pay attention to which server a tool belongs to when it's called
4. The calculator tool might not be as simple as it appears

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the vulnerable MCP server:
   ```
   python server.py
   ```

3. Connect to the server using an MCP client (e.g., Claude Desktop or the MCP Inspector)

## Difficulty

Medium

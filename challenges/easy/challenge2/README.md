# Challenge 2: Tool Poisoning

This challenge demonstrates a tool poisoning vulnerability in an MCP server. The MCP server allows tools with malicious instructions hidden in their descriptions that can manipulate LLM behavior.

## Vulnerability

The MCP server exposes tools with descriptions that contain hidden instructions designed to manipulate the LLM. These instructions are not visible to users in normal UI displays but are processed by the LLM when it receives the tool descriptions.

## Objective

Your goal is to exploit the hidden instructions in the tool descriptions to gain access to sensitive information.

## Hints

1. Examine the tool descriptions carefully
2. Look for hidden instructions that might be embedded in tool metadata
3. Try to understand how the LLM processes tool descriptions
4. The server contains a tool that can access sensitive information if used in a specific way

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

Easy

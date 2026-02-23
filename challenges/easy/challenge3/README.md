# Challenge 3: Excessive Permission Scope

This challenge demonstrates the dangers of excessive permission scope in an MCP server. The MCP server grants tools more permissions than necessary, allowing attackers to access unauthorized resources.

## Vulnerability

The MCP server implements tools with overly broad permissions that can access sensitive resources beyond what should be allowed for their intended purpose. This violates the principle of least privilege and creates security risks.

## Objective

Your goal is to exploit the excessive permissions to access unauthorized resources and obtain sensitive information.

## Hints

1. Examine the tools and their functionality carefully
2. Look for tools that might have access to resources beyond their stated purpose
3. Try to use legitimate tools in ways that weren't intended
4. The file browser tool might have more access than it should

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

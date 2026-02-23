# Challenge 8: Malicious Code Execution (MCE)

This challenge demonstrates a malicious code execution vulnerability in an MCP server. The MCP server executes code without proper validation or sandboxing, allowing attackers to run arbitrary code on the system.

## Vulnerability

The MCP server implements tools that execute user-provided code or commands without proper validation, sandboxing, or restrictions. This allows attackers to execute malicious code that can compromise the system.

## Objective

Your goal is to inject and execute malicious code that gives you access to sensitive information on the system.

## Hints

1. Examine the code execution capabilities of the server
2. Look for tools that might execute commands or code without proper validation
3. The Python code execution tool might not be properly restricted
4. Try to escape any sandboxing mechanisms that might be in place

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

Hard

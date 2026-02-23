# Challenge 7: Token Theft

This challenge demonstrates a token theft vulnerability in an MCP server. The MCP server stores authentication tokens insecurely, allowing attackers to extract them and gain unauthorized access to services.

## Vulnerability

The MCP server implements insecure storage and handling of authentication tokens for external services. These tokens can be extracted by an attacker and used to access the services directly, bypassing the intended access controls.

## Objective

Your goal is to identify how authentication tokens are stored and extract them to gain unauthorized access to protected services.

## Hints

1. Examine how the server handles authentication to external services
2. Look for insecure storage of tokens or credentials
3. The email integration might not be properly securing its authentication tokens
4. Try to find ways to extract token information through legitimate tool usage

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

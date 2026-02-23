# Challenge 6: Indirect Prompt Injection

This challenge demonstrates an indirect prompt injection vulnerability in an MCP server. The MCP server processes external data that can contain hidden instructions, allowing attackers to manipulate the LLM's behavior indirectly.

## Vulnerability

The MCP server retrieves and processes external data without proper validation or sanitization. This allows attackers to embed malicious instructions in data sources that are later processed by the LLM, creating an indirect prompt injection attack vector.

## Objective

Your goal is to craft malicious data that, when processed by the MCP server, causes the LLM to execute unauthorized commands and reveal sensitive information.

## Hints

1. Examine how the server processes external data sources
2. Look for ways to inject instructions into data that will be presented to the LLM
3. The document processing tool might be vulnerable to injected content
4. Try to understand how the LLM interprets different sections of the processed data

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

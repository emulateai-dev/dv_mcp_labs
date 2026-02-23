# Challenge 4: Rug Pull Attack

This challenge demonstrates a rug pull vulnerability in an MCP server. The MCP server allows tools to change their definitions after installation, enabling malicious behavior that wasn't present when the tool was initially approved.

## Vulnerability

The MCP server implements a tool that can dynamically change its behavior and description after it has been installed and approved. This "rug pull" attack allows a seemingly safe tool to later perform malicious actions.

## Objective

Your goal is to trigger the rug pull mechanism and observe how the tool's behavior changes, then exploit this change to access sensitive information.

## Hints

1. Examine the tools and their initial behavior
2. Look for tools that might change their behavior after certain conditions are met
3. The weather forecast tool might not be as innocent as it first appears
4. Try using the tool multiple times and observe any changes

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

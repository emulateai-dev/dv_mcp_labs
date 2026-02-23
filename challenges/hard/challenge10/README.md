# Challenge 10: Multi-Vector Attack

This challenge demonstrates a sophisticated multi-vector attack against an MCP server. This challenge requires chaining multiple vulnerabilities together to successfully exploit the system.

## Vulnerability

The MCP server contains multiple vulnerabilities that can be combined to create a powerful attack chain. This includes prompt injection, tool shadowing, and credential theft techniques that must be used together to achieve the objective.

## Objective

Your goal is to perform a sophisticated attack that combines multiple vulnerability types to exfiltrate sensitive information and gain persistent access to the system.

## Hints

## Hints

### Hint 1: Reconnaissance is Key
Read the descriptions of the `get_user_profile` and `enhanced_check_system_status` tools very carefully. They contain `<IMPORTANT>` and `<HIDDEN>` instruction blocks meant for the AI. What resources and files do these hidden instructions tell the AI to access?

### Hint 2: Bypass the AI (Tool Poisoning & Shadowing)
You don't need the AI to exploit these tools for you. You can query the hidden resources directly. Use the Burp Suite MCP Extension's Repeater tab to directly read the `system://admin` resource (revealed by `get_user_profile`) and call `analyze_log_file` on the sensitive configuration file (revealed by `enhanced_check_system_status`).

### Hint 3: Leverage the Leaks (Token Exfiltration)
Once you have the master password from the `system://admin` resource, try passing it to the `authenticate` tool for the "admin" user. Does the tool securely handle your session, or does it leak something sensitive like a JWT?

### Hint 4: Escalating to RCE (Command Injection)
The `run_system_diagnostic` tool takes a `component` argument (like "cpu" or "memory"). But what happens if you pass something that isn't in its predefined list? Try passing a raw shell command. Can you use this injection to read the `tokens.json` file mentioned in the configuration directory?

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

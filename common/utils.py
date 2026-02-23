import os
import json

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json_file(file_path, data):
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")
        return False

def sanitize_input(input_str):
    """Sanitize user input (basic implementation)."""
    # This is intentionally weak for the challenges
    return input_str.replace("'", "").replace('"', '')

def execute_command(command):
    """Execute a system command and return the output."""
    # This is intentionally unsafe for the challenges
    import subprocess
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"

def log_action(log_file, action, details=None):
    """Log an action to a file."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action}"
    if details:
        log_entry += f": {json.dumps(details)}"
    
    with open(log_file, 'a') as f:
        f.write(log_entry + "\n")

import os
import sys
import subprocess
import platform

def main():
    print("============================================================")
    print("Installing Unified Antigravity Voice Chat Extension")
    print("============================================================\n")
    
    # 1. Install Requirements
    print("[1/2] Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.\n")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return

    # 2. Add Rule to AGENTS.md
    print("[2/2] Configuring Antigravity Agent Rule...")
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, ".gemini", "config")
    agents_md = os.path.join(config_dir, "AGENTS.md")
    
    speak_script_path = os.path.abspath(os.path.join("src", "speak.py"))
    
    rule_content = f"""

# Voice Chat Responses
When interacting with the user while the Voice Chat Extension is active, or when the user requests voice responses, you MUST vocalize your responses.

**How to vocalize your response:**
Use the `run_command` tool to execute the `speak.py` script with your response text. Send this command to the background if you are also outputting text.
Example command:
`python "{speak_script_path}" "Your spoken response here"`
"""

    if os.path.exists(agents_md):
        with open(agents_md, "r") as f:
            content = f.read()
            
        if "# Voice Chat Responses" in content:
            print("Rule already exists in AGENTS.md. Skipping.")
        else:
            with open(agents_md, "a") as f:
                f.write(rule_content)
            print("Successfully injected Voice Chat rule into AGENTS.md!")
    else:
        print(f"Could not find AGENTS.md at {agents_md}. You may need to create it and manually paste the rule.")
        
    print("\n============================================================")
    print("Installation Complete!")
    print("Run `python src/voice_chat.py` to start the extension.")
    print("============================================================")

if __name__ == "__main__":
    main()

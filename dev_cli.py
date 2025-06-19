#!/usr/bin/env python3

import os
import sys
import json
import yaml
import subprocess
import requests
import site
from pathlib import Path
from typing import Dict, List, Any, Optional

# Check if we're running in a virtual environment
def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

# Try to use the virtual environment if available
script_dir = Path(__file__).parent.absolute()
venv_path = script_dir / "venv"
if venv_path.exists() and not is_venv():
    print(f"🧪 Detected virtual environment at {venv_path}")
    venv_python = venv_path / "bin" / "python"
    if venv_python.exists():
        print(f"🔄 Re-executing with virtual environment Python: {venv_python}")
        os.execl(str(venv_python), str(venv_python), *sys.argv)

try:
    import anthropic
except ImportError:
    print("❌ Anthropic SDK not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "anthropic>=0.20.0"], check=True)
    import anthropic

class DevAssistant:
    def __init__(self):
        self.config_path = self.find_config_file()
        self.config = self.load_config()
        # Get the Anthropic API key from environment variable
        # Used with the Anthropic SDK to call Claude AI
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")

    def find_config_file(self) -> str:
        """Find the configuration file in the current directory."""
        possible_paths = [
            ".dev-cheat.yaml",
            ".dev-cheat.yml",
            "dev-commands.yaml",
            "dev-commands.yml"
        ]
        
        for file_path in possible_paths:
            if Path(file_path).exists():
                return file_path
        
        raise FileNotFoundError("No dev-commands.yaml file found in current directory")

    def load_config(self) -> dict:
        """Load the configuration from the YAML file."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Error loading config file: {str(e)}")

    async def execute_command(self, command: str, args: List[str] = None) -> None:
        """Execute a command with optional arguments."""
        if args is None:
            args = []
        
        full_command = " ".join([command] + args)
        
        # Check if it's a quick command first
        if self.config.get("quick_commands") and command in self.config["quick_commands"]:
            return self.execute_quick_command(command)
        
        # Check if it's an AI command
        if self.config.get("ai_commands") and command in self.config["ai_commands"]:
            return await self.execute_ai_command(command, args)
        
        # Check if it's a workflow
        if self.config.get("workflows") and command in self.config["workflows"]:
            return await self.execute_workflow(command, args)
        
        # Check custom vocabulary
        if self.config.get("vocabulary") and full_command in self.config["vocabulary"]:
            return await self.execute_ai_command("custom", [self.config["vocabulary"][full_command]])

        # Default: send to AI for interpretation
        return await self.execute_ai_command("interpret", [full_command])

    def execute_quick_command(self, command: str) -> None:
        """Execute a configured quick command."""
        cmd = self.config["quick_commands"][command]
        print(f"🚀 Executing: {cmd['description']}")
        
        try:
            for action in cmd["actions"]:
                print(f"  → {action}")
                if not action.startswith("echo "):
                    subprocess.run(action, shell=True, check=True)
                else:
                    print(action.replace("echo ", ""))
            print("✅ Command completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {str(e)}")
            sys.exit(1)

    async def execute_ai_command(self, command: str, args: List[str]) -> None:
        """Execute a command that requires AI processing."""
        if not self.anthropic_api_key:
            print("❌ ANTHROPIC_API_KEY environment variable not set")
            print("Please set your Claude API key: export ANTHROPIC_API_KEY=your_key_here")
            sys.exit(1)

        print("🤖 Processing with Claude AI...")
        
        prompt = self.build_ai_prompt(command, args)
        
        try:
            response = await self.call_claude_api(prompt)
            return self.execute_ai_response(response)
        except Exception as e:
            print(f"❌ AI command failed: {str(e)}")
            sys.exit(1)

    def build_ai_prompt(self, command: str, args: List[str]) -> str:
        """Build a prompt for Claude API."""
        context = self.get_project_context()
        command_context = self.get_command_context(command, args)
        
        return f"""You are a development assistant for this project. Here's the context:

PROJECT CONTEXT:
{json.dumps(context, indent=2)}

COMMAND: {command}
ARGS: {' '.join(args)}

COMMAND CONTEXT:
{command_context}

Based on the project context and command, provide executable actions. If you're generating code, make it production-ready and follow the specified standards.

Respond in this format:
ACTIONS:
- [list of shell commands to execute]

CODE:
[any code files to create/modify]

EXPLANATION:
[brief explanation of what you're doing]"""

    def get_project_context(self) -> Dict[str, Any]:
        """Get project context information."""
        return {
            "project": self.config.get("project", {}),
            "standards": self.config.get("project", {}).get("standards", {}),
            "tools": self.config.get("project", {}).get("tools", {}),
            "currentDirectory": os.getcwd(),
            "files": self.get_relevant_files()
        }

    def get_relevant_files(self) -> List[str]:
        """Get a list of relevant files in the project."""
        try:
            # Get basic project structure
            result = subprocess.run(
                "find . -type f -name '*.py' -o -name '*.html' -o -name '*.js' -o -name '*.css' | head -20",
                shell=True, capture_output=True, text=True
            )
            files = result.stdout.strip().split("\n")
            return [f for f in files if f and "node_modules" not in f and "__pycache__" not in f]
        except:
            return []

    def get_command_context(self, command: str, args: List[str]) -> str:
        """Get context for a specific command."""
        if (self.config.get("ai_commands") and command in self.config["ai_commands"]):
            cmd_config = self.config["ai_commands"][command]
            context_needed = cmd_config.get("context_needed", [])
            context_str = ", ".join(context_needed) if context_needed else "none"
            return f"Template: {cmd_config.get('template', '')}\nContext needed: {context_str}"
        return f"General command interpretation needed for: {command} {' '.join(args)}"

    async def call_claude_api(self, prompt: str) -> str:
        """Call Claude API with the given prompt using the Anthropic SDK."""
        if not self.anthropic_api_key:
            raise Exception("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize the Anthropic client
        client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        
        try:
            # Use the client to create a message
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Return the response text
            return message.content[0].text
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

    def execute_ai_response(self, response: str) -> None:
        """Execute actions from AI response."""
        print("📝 Claude Response:")
        print(response)
        
        # Parse actions from response
        import re
        action_match = re.search(r"ACTIONS:\s*([\s\S]*?)(?=CODE:|EXPLANATION:|$)", response)
        if action_match:
            actions_text = action_match.group(1).strip()
            actions = [
                line.replace("-", "", 1).strip()
                for line in actions_text.split("\n")
                if line.strip().startswith("-")
            ]
            
            if actions:
                print("\n🔧 Executing actions:")
                for action in actions:
                    print(f"  → {action}")
                    try:
                        subprocess.run(action, shell=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"    ❌ Failed: {str(e)}")

        # Handle code generation
        code_match = re.search(r"CODE:\s*([\s\S]*?)(?=EXPLANATION:|$)", response)
        if code_match:
            print("\n📄 Generated code:")
            print(code_match.group(1).strip())

    async def execute_workflow(self, workflow: str, args: List[str]) -> None:
        """Execute a workflow sequence."""
        wf = self.config["workflows"][workflow]
        print(f"🔄 Starting workflow: {wf['description']}")
        
        # For now, treat workflow steps as AI commands
        steps_prompt = f"Execute this workflow: {', '.join(wf['steps'])}"
        return await self.execute_ai_command("workflow", [steps_prompt] + args)

    def show_help(self) -> None:
        """Display help information."""
        quick_commands = ""
        if self.config.get("quick_commands"):
            quick_commands = "\n".join(
                f"  {cmd.ljust(15)} - {config['description']}"
                for cmd, config in self.config["quick_commands"].items()
            )
        
        ai_commands = ""
        if self.config.get("ai_commands"):
            ai_commands = "\n".join(
                f"  {cmd.ljust(15)} - {config['description']}" 
                for cmd, config in self.config["ai_commands"].items()
                if isinstance(config, dict) and "description" in config
            )
        
        workflows = ""
        if self.config.get("workflows"):
            workflows = "\n".join(
                f"  {cmd.ljust(15)} - {config['description']}"
                for cmd, config in self.config["workflows"].items()
            )
        
        help_text = f"""
🚀 Dev Assistant CLI

USAGE:
  dev <command> [args...]

QUICK COMMANDS:
{quick_commands}

AI COMMANDS:
{ai_commands}

WORKFLOWS:
{workflows}

EXAMPLES:
  dev build                    # Run production build
  dev create component Button  # Generate new component
  dev fix                      # Auto-fix linting issues
  dev analyze src/App.py       # Analyze specific file

Set ANTHROPIC_API_KEY environment variable for AI commands.
    """
        print(help_text)

async def main():
    """CLI entry point."""
    args = sys.argv[1:]
    
    if not args or args[0] in ["--help", "-h"]:
        try:
            assistant = DevAssistant()
            assistant.show_help()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("\nCreate a .dev-commands.yaml file to get started!")
        return
    
    try:
        assistant = DevAssistant()
        command, *command_args = args
        await assistant.execute_command(command, command_args)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

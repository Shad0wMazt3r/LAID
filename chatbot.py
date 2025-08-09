#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import subprocess
import os
import re
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
import colorama
from colorama import Fore, Back, Style

colorama.init()
console = Console()

class LMStudioChatbot:
    def __init__(self):
        self.config = self.load_config()
        self.base_url = self.config["lm_studio"]["base_url"]
        self.model = self.config["lm_studio"]["current_model"]
        self.messages = []
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "City name or location"}
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute a shell command (requires user approval)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command to execute"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string", "description": "Path to the file"}
                        },
                        "required": ["filepath"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List files in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "description": "Directory path"}
                        },
                        "required": ["directory"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file (requires user approval)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string", "description": "Path to the file"},
                            "content": {"type": "string", "description": "Content to write"}
                        },
                        "required": ["filepath", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Edit a file by replacing text (requires user approval)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string", "description": "Path to the file"},
                            "old_text": {"type": "string", "description": "Text to replace"},
                            "new_text": {"type": "string", "description": "New text"}
                        },
                        "required": ["filepath", "old_text", "new_text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "switch_model",
                    "description": "Switch to a different AI model",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "model_id": {"type": "string", "description": "Model ID to switch to"}
                        },
                        "required": ["model_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_models",
                    "description": "List available AI models",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    def load_config(self):
        try:
            with open("laid.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "lm_studio": {
                    "base_url": "http://localhost:1234/v1/",
                    "current_model": "google/gemma-3-4b"
                }
            }
    
    def fetch_models(self):
        try:
            req = urllib.request.Request(f"{self.base_url}models")
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('data', [])
        except Exception as e:
            console.print(f"[red]Error fetching models: {e}[/red]")
            return []
    
    def save_config(self):
        with open("laid.json", "w") as f:
            json.dump(self.config, f, indent=2)
    
    def switch_model(self, model_id):
        available_models = self.fetch_models()
        available_ids = [m["id"] for m in available_models]
        if model_id in available_ids:
            self.config["lm_studio"]["current_model"] = model_id
            self.model = model_id
            self.save_config()
            return True
        return False
    
    def get_weather(self, location):
        # Mock weather data for testing
        weather_data = {
            "paris": {"temperature": "22°C", "condition": "Sunny", "humidity": "65%"},
            "london": {"temperature": "18°C", "condition": "Cloudy", "humidity": "80%"},
            "tokyo": {"temperature": "25°C", "condition": "Rainy", "humidity": "90%"}
        }
        
        location_key = location.lower()
        if location_key in weather_data:
            return weather_data[location_key]
        else:
            return {"error": f"Weather data not available for {location}"}
    
    def execute_command(self, command):
        console.print()  # Ensure newline
        console.print(Panel(f"🚀 Execute Command: [bold cyan]{command}[/bold cyan]\n\n[yellow]Type 'y' to approve or 'n' to deny[/yellow]", 
                           title="[red]⚠️  APPROVAL REQUIRED[/red]", border_style="red"))
        approval = Prompt.ask("[bold yellow]Approve[/bold yellow]", choices=["y", "n"], default="n")
        
        if approval == 'y':
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
            except subprocess.TimeoutExpired:
                return {"error": "Command timed out"}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "Command execution denied by user"}
    
    def read_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return {"content": f.read()}
        except Exception as e:
            return {"error": str(e)}
    
    def list_files(self, directory):
        try:
            files = os.listdir(directory)
            return {"files": files}
        except Exception as e:
            return {"error": str(e)}
    
    def write_file(self, filepath, content):
        console.print()  # Ensure newline
        console.print(Panel(f"📝 Write File: [bold green]{filepath}[/bold green]\n[dim]{content[:100]}...[/dim]\n\n[yellow]Type 'y' to approve or 'n' to deny[/yellow]", 
                           title="[red]⚠️  APPROVAL REQUIRED[/red]", border_style="red"))
        approval = Prompt.ask("[bold yellow]Approve[/bold yellow]", choices=["y", "n"], default="n")
        
        if approval == 'y':
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"success": f"File written: {filepath}"}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "File write denied by user"}
    
    def edit_file(self, filepath, old_text, new_text):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Replace", style="red")
        table.add_column("With", style="green")
        table.add_row(old_text[:50] + "...", new_text[:50] + "...")
        
        console.print()  # Ensure newline
        console.print(Panel(table, title=f"[red]⚠️  EDIT FILE: {filepath}[/red]", border_style="red"))
        console.print("[yellow]Type 'y' to approve or 'n' to deny[/yellow]")
        approval = Prompt.ask("[bold yellow]Approve[/bold yellow]", choices=["y", "n"], default="n")
        
        if approval == 'y':
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if old_text not in content:
                    return {"error": "Text to replace not found"}
                
                new_content = content.replace(old_text, new_text)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return {"success": f"File edited: {filepath}"}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "File edit denied by user"}
    
    def handle_tool_call(self, tool_call):
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        if function_name == "get_weather":
            if "location" not in arguments:
                return {"error": "Missing required parameter: location"}
            return self.get_weather(arguments["location"])
        elif function_name == "execute_command":
            if "command" not in arguments:
                return {"error": "Missing required parameter: command"}
            return self.execute_command(arguments["command"])
        elif function_name == "read_file":
            if "filepath" not in arguments:
                return {"error": "Missing required parameter: filepath"}
            return self.read_file(arguments["filepath"])
        elif function_name == "list_files":
            if "directory" not in arguments:
                return {"error": "Missing required parameter: directory"}
            return self.list_files(arguments["directory"])
        elif function_name == "write_file":
            if "filepath" not in arguments or "content" not in arguments:
                return {"error": "Missing required parameters: filepath, content"}
            return self.write_file(arguments["filepath"], arguments["content"])
        elif function_name == "edit_file":
            if "filepath" not in arguments or "old_text" not in arguments or "new_text" not in arguments:
                return {"error": "Missing required parameters: filepath, old_text, new_text"}
            return self.edit_file(arguments["filepath"], arguments["old_text"], arguments["new_text"])
        elif function_name == "switch_model":
            if "model_id" not in arguments:
                return {"error": "Missing required parameter: model_id"}
            success = self.switch_model(arguments["model_id"])
            if success:
                return {"success": f"Switched to model: {arguments['model_id']}"}
            else:
                return {"error": "Model not found"}
        elif function_name == "list_models":
            models = self.fetch_models()
            formatted_models = [{"name": m.get("id", "Unknown").split("/")[-1], "id": m["id"]} for m in models]
            return {"models": formatted_models, "current_model": self.model}
        return {"error": f"Unknown function: {function_name}"}
    
    def chat_stream(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": 2000,
            "temperature": 0.7,
            "stream": True,
            "tools": self.tools
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{self.base_url}chat/completions",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            full_response = ""
            tool_calls_by_index = {}
            
            with urllib.request.urlopen(req) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and chunk['choices']:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content = delta['content']
                                    console.print(content, end='', style="white")
                                    full_response += content
                                elif 'tool_calls' in delta:
                                    if delta['tool_calls']:
                                        for tc in delta['tool_calls']:
                                            index = tc.get('index', 0)
                                            if index not in tool_calls_by_index:
                                                tool_calls_by_index[index] = {
                                                    'id': tc.get('id', ''),
                                                    'type': tc.get('type', 'function'),
                                                    'function': {
                                                        'name': tc.get('function', {}).get('name', ''),
                                                        'arguments': ''
                                                    }
                                                }
                                            
                                            if 'function' in tc and 'arguments' in tc['function']:
                                                tool_calls_by_index[index]['function']['arguments'] += tc['function']['arguments']
                                            if 'function' in tc and 'name' in tc['function']:
                                                tool_calls_by_index[index]['function']['name'] = tc['function']['name']
                                            if 'id' in tc:
                                                tool_calls_by_index[index]['id'] = tc['id']
                        except json.JSONDecodeError:
                            continue
            
            # Handle tool calls
            tool_calls = list(tool_calls_by_index.values())
            
            valid_tool_calls = []
            for tool_call in tool_calls:
                if (tool_call['function']['name'] and 
                    tool_call['function']['arguments'] and
                    tool_call['id']):
                    valid_tool_calls.append(tool_call)
            
            if valid_tool_calls:
                self.messages.append({"role": "assistant", "content": full_response, "tool_calls": valid_tool_calls})
                
                for tool_call in valid_tool_calls:
                    try:
                        function_name = tool_call['function']['name']
                        args_str = tool_call['function']['arguments']
                        # Execute tool without spinner to show approval prompts
                        arguments = json.loads(args_str)
                        result = self.handle_tool_call(tool_call)
                        
                        if "error" in result:
                            console.print(f"[red]❌ Error: {result['error']}[/red]")
                        else:
                            if function_name == "read_file" and "content" in result:
                                console.print()
                                syntax = Syntax(result["content"][:500], "text", theme="monokai", line_numbers=True)
                                console.print(Panel(syntax, title=f"📄 File Content", border_style="blue"))
                            elif function_name == "list_files" and "files" in result:
                                console.print()
                                files_text = "\n".join([f"📁 {f}" if os.path.isdir(f) else f"📄 {f}" for f in result["files"]])
                                console.print(Panel(files_text, title="📂 Directory Contents", border_style="blue"))
                            elif function_name == "list_models" and "models" in result:
                                console.print()
                                table = Table(show_header=True, header_style="bold cyan")
                                table.add_column("Model Name", style="green")
                                table.add_column("Model ID", style="blue")
                                table.add_column("Status", style="yellow")
                                
                                for model in result["models"]:
                                    status = "✅ Current" if model["id"] == result["current_model"] else "⏸️ Available"
                                    table.add_row(model["name"], model["id"], status)
                                
                                console.print(Panel(table, title="🤖 Available Models", border_style="cyan"))
                            else:
                                console.print(f"[green]✅ {result}[/green]")
                        
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result)
                        })
                    except Exception as e:
                        console.print(f"[red]💥 Tool Error: {e}[/red]")
                        console.print(f"[dim]Function: {tool_call['function']['name']}[/dim]")
                        console.print(f"[dim]Arguments: {tool_call['function']['arguments']}[/dim]")
                
                # Get follow-up response with tool results
                return self.chat_stream("")
            else:
                self.messages.append({"role": "assistant", "content": full_response})
                return full_response
        except Exception as e:
            console.print(f"[red]Chat error: {e}[/red]")
            return f"Error: {e}"

def main():
    # Animated startup
    console.clear()
    
    # Title animation
    title = Text("🤖 LAID 🚀", style="bold magenta")
    console.print(Align.center(title))
    console.print(Align.center("[dim]Local AI-assisted Development[/dim]"))
    console.print(Rule("[blue]Ready to Chat[/blue]"))
    
    chatbot = LMStudioChatbot()
    
    # Tool info panel
    tools_info = """🌤️  Weather Info  📁 File Operations  🚀 Command Execution
📖 Read Files    📝 Write Files     ✏️  Edit Files
🤖 Model Switch  📊 List Models"""
    console.print(Panel(tools_info, title="[cyan]Available Tools[/cyan]", border_style="cyan"))
    
    # Show current model
    console.print(f"[dim]Current Model: {chatbot.model}[/dim]")
    
    while True:
        console.print()
        user_input = Prompt.ask("[bold blue]You[/bold blue]").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            console.print("[yellow]👋 Goodbye![/yellow]")
            break
        
        if not user_input:
            continue
        
        console.print("[bold green]Assistant:[/bold green] ", end="")
        response = chatbot.chat_stream(user_input)
        if response:
            console.print()

if __name__ == "__main__":
    main()
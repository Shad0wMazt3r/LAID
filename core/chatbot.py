import urllib.request
import json
import signal
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from config.config_manager import ConfigManager
from models.model_manager import ModelManager
from tools.tool_handler import ToolHandler
from modes.mode_manager import ModeManager

console = Console()

class LMStudioChatbot:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.model_manager = ModelManager(self.config_manager)
        self.tool_handler = ToolHandler()
        self.mode_manager = ModeManager()
        self.paused = False
        signal.signal(signal.SIGINT, self._handle_interrupt)
        
        instructions = self.config_manager.get_instructions()
        system_info = self.config_manager.get_system_info()

        initial_information = instructions + "\n" + system_info
        self.messages = [{"role": "system", "content": initial_information}]
        
        self.tools = [
            # {
            #     "type": "function",
            #     "function": {
            #         "name": "get_weather",
            #         "description": "Get weather information for a location",
            #         "parameters": {
            #             "type": "object",
            #             "properties": {
            #                 "location": {"type": "string", "description": "City name or location"}
            #             },
            #             "required": ["location"]
            #         }
            #     }
            # },
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
                    "name": "change_directory",
                    "description": "Change your current directory (requires user approval)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directorypath": {"type": "string", "description": "Path to the directory"}
                        },
                        "required": ["directorypath"]
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
            }
        ]
    
    def chat_stream(self, user_input):
        if user_input.strip().startswith("/switch_model"):
            self.model_manager.handle_switch_model_command(user_input.strip())
            return None
        
        if user_input.strip().startswith("/mode"):
            return self._handle_mode_command(user_input.strip())
        
        if user_input.strip() == "/pause":
            return self._handle_pause_command()
        
        # Reset pause flag
        if self.paused:
            self.paused = False
            console.print(f"[green]Resuming with your guidance...[/green]")
        
        # Add mode prompt if active
        mode_prompt = self.mode_manager.get_current_mode_prompt()
        if mode_prompt:
            enhanced_input = mode_prompt + "\n\nUser Input: " + user_input
            self.messages.append({"role": "user", "content": enhanced_input})
        else:
            self.messages.append({"role": "user", "content": user_input})
        
        payload = {
            "model": self.config_manager.get_current_model(),
            "messages": self.messages,
            "max_tokens": 2000,
            "temperature": 0.1,
            "stream": True,
            "tools": self.tools
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{self.config_manager.get_base_url()}chat/completions",
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
                                    if self.paused:
                                        break
                                    content = delta['content']
                                    console.print(content, end='', style="dim white")
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
                        result = self.tool_handler.handle_tool_call(tool_call)
                        self.tool_handler.display_tool_result(function_name, result)
                        
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result)
                        })
                    except Exception as e:
                        console.print(f"[red]💥 Tool Error: {e}[/red]")
                        console.print(f"[dim]Function: {tool_call['function']['name']}[/dim]")
                        console.print(f"[dim]Arguments: {tool_call['function']['arguments']}[/dim]")
                
                return self.chat_stream("")
            else:
                if self.paused:
                    self.messages.append({"role": "assistant", "content": full_response})
                    return "PAUSED"
                self.messages.append({"role": "assistant", "content": full_response})
                console.clear()
                console.print("─" * 50)
                console.print(Markdown(full_response))
                return full_response
        except Exception as e:
            console.print(f"[red]Chat error: {e}[/red]")
            return f"Error: {e}"
    
    def _handle_mode_command(self, command):
        parts = command.split()
        if len(parts) == 1:
            # Show current mode and available modes
            current = self.mode_manager.current_mode or "None"
            available = ", ".join(self.mode_manager.get_available_modes())
            console.print(f"[cyan]Current mode: {current}[/cyan]")
            console.print(f"[cyan]Available modes: {available}[/cyan]")
            console.print(f"[dim]Usage: /mode <mode_name> or /mode clear[/dim]")
        elif len(parts) == 2:
            mode_name = parts[1]
            if mode_name == "clear":
                self.mode_manager.clear_mode()
                console.print(f"[green]Mode cleared[/green]")
            elif self.mode_manager.set_mode(mode_name):
                console.print(f"[green]Mode set to: {mode_name}[/green]")
            else:
                console.print(f"[red]Unknown mode: {mode_name}[/red]")
        return None
    
    def _handle_pause_command(self):
        console.print(f"[yellow]🛑 Agent paused. Provide guidance or instructions to continue.[/yellow]")
        console.print(f"[dim]The agent will incorporate your next message into its context.[/dim]")
        return None
    
    def _handle_interrupt(self, signum, frame):
        self.paused = True
        console.print(f"\n[yellow]🛑 Agent paused by Ctrl+C. Provide guidance to continue.[/yellow]")
        console.print(f"[dim]Your next input will steer the agent.[/dim]")
        return "PAUSED"
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
from .ctf_session_manager import CTFSessionManager

console = Console()

class LMStudioChatbot:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.model_manager = ModelManager(self.config_manager)
        self.tool_handler = ToolHandler()
        self.mode_manager = ModeManager()
        self.ctf_session_manager = CTFSessionManager()
        self.paused = False
        signal.signal(signal.SIGINT, self._handle_interrupt)

        # Load current CTF session if exists
        current_session = self.config_manager.get_current_ctf_session()
        if current_session:
            self.ctf_session_manager.set_current_session(current_session)
        
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
                    "description": "Execute a shell command autonomously",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command to execute"},
                            "expect_prompts": {
                                "type": "array",
                                "description": "List of expected prompts and responses for interactive commands",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "prompt": {"type": "string", "description": "Text to expect from the command"},
                                        "response": {"type": "string", "description": "Response to send when prompt is detected"}
                                    },
                                    "required": ["prompt", "response"]
                                }
                            },
                            "timeout": {"type": "integer", "description": "Command timeout in seconds", "default": 30}
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
            },
            {
                "type": "function",
                "function": {
                    "name": "open_browser",
                    "description": "Open a URL in the default browser",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to open"}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search the web using SearXNG",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_cve",
                    "description": "Search for CVE vulnerability information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cve_id": {"type": "string", "description": "CVE ID (e.g., CVE-2021-44228 or 2021-44228)"}
                        },
                        "required": ["cve_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_cve_by_keyword",
                    "description": "Search for CVEs by keyword (e.g., 'apache', 'sql injection')",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string", "description": "Keyword to search for in CVE descriptions"}
                        },
                        "required": ["keyword"]
                    }
                }
            },
            # Security tools for CTF
            {
                "type": "function",
                "function": {
                    "name": "nmap_scan",
                    "description": "Perform NMAP network scan on target",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "description": "Target IP, hostname, or network range"},
                            "scan_type": {"type": "string", "description": "Scan type: basic, full, vuln, udp, stealth", "default": "basic"},
                            "options": {"type": "string", "description": "Additional NMAP options"}
                        },
                        "required": ["target"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_fuzz_payloads",
                    "description": "Generate fuzzing payloads for testing vulnerabilities",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "payload_type": {"type": "string", "description": "Type of payloads: sql, xss, command, path_traversal, buffer_overflow, format_string", "default": "sql"},
                            "count": {"type": "integer", "description": "Number of payloads to generate", "default": 50}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fuzz_web_parameter",
                    "description": "Fuzz a web application parameter for vulnerabilities",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "Target URL"},
                            "param_name": {"type": "string", "description": "Parameter name to fuzz"},
                            "payloads": {"type": "array", "description": "Custom payloads to use (optional)"},
                            "method": {"type": "string", "description": "HTTP method: GET or POST", "default": "GET"},
                            "headers": {"type": "object", "description": "Custom headers"}
                        },
                        "required": ["url", "param_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_metasploit_exploit",
                    "description": "Execute a Metasploit exploit module",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "module_name": {"type": "string", "description": "Metasploit module name (e.g., exploit/windows/smb/ms17_010_eternalblue)"},
                            "options": {"type": "object", "description": "Module options as key-value pairs"}
                        },
                        "required": ["module_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_custom_exploit",
                    "description": "Execute custom exploit code",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "exploit_code": {"type": "string", "description": "Python exploit code to execute"},
                            "target_info": {"type": "object", "description": "Target information (IP, port, etc.)"}
                        },
                        "required": ["exploit_code", "target_info"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_exploit_template",
                    "description": "Generate an exploit template",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "exploit_type": {"type": "string", "description": "Type of exploit: buffer_overflow, sql_injection, command_injection", "default": "buffer_overflow"}
                        }
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

        if user_input.strip().startswith("/ctf"):
            return self._handle_ctf_command(user_input.strip())

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

        # Check cache if enabled
        cached_response = None
        if self.config_manager.is_cache_enabled():
            cache_key = self.ctf_session_manager.get_cache_key({
                "messages": self.messages,
                "model": self.config_manager.get_current_model()
            })
            cached_response = self.ctf_session_manager.get_cached_response(cache_key)

        if cached_response:
            console.clear()
            console.print("─" * 50)
            console.print(Markdown(cached_response))
            console.print(f"[dim]💾 Response loaded from cache[/dim]")
            self.messages.append({"role": "assistant", "content": cached_response})
            return cached_response

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

                # Cache the response if caching is enabled
                if self.config_manager.is_cache_enabled():
                    cache_key = self.ctf_session_manager.get_cache_key({
                        "messages": self.messages[:-1],  # Exclude the assistant message we're about to add
                        "model": self.config_manager.get_current_model()
                    })
                    self.ctf_session_manager.cache_response(cache_key, full_response)

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
    
    def _handle_ctf_command(self, command):
        parts = command.split()
        if len(parts) < 2:
            # Show CTF help
            current_session = self.ctf_session_manager.current_session or "None"
            console.print(f"[cyan]Current CTF session: {current_session}[/cyan]")
            console.print(f"[cyan]Available commands:[/cyan]")
            console.print(f"[dim]/ctf create <ctf_name> [challenge_name] - Create new CTF session[/dim]")
            console.print(f"[dim]/ctf switch <session_id> - Switch to existing session[/dim]")
            console.print(f"[dim]/ctf list - List all sessions[/dim]")
            console.print(f"[dim]/ctf status - Show current session status[/dim]")
            console.print(f"[dim]/ctf log <reasoning|path|finding> <details> - Log information[/dim]")
            return None

        subcommand = parts[1]

        if subcommand == "create":
            if len(parts) < 3:
                console.print(f"[red]Usage: /ctf create <ctf_name> [challenge_name][/red]")
                return None
            ctf_name = parts[2]
            challenge_name = parts[3] if len(parts) > 3 else None
            session_id = self.ctf_session_manager.create_session(ctf_name, challenge_name)
            self.config_manager.set_current_ctf_session(session_id)
            console.print(f"[green]Created CTF session: {session_id}[/green]")

        elif subcommand == "switch":
            if len(parts) < 3:
                console.print(f"[red]Usage: /ctf switch <session_id>[/red]")
                return None
            session_id = parts[2]
            if self.ctf_session_manager.set_current_session(session_id):
                self.config_manager.set_current_ctf_session(session_id)
                console.print(f"[green]Switched to CTF session: {session_id}[/green]")
            else:
                console.print(f"[red]Session not found: {session_id}[/red]")

        elif subcommand == "list":
            sessions = self.ctf_session_manager.list_sessions()
            if sessions:
                console.print(f"[cyan]Available CTF sessions:[/cyan]")
                for session in sessions:
                    summary = self.ctf_session_manager.get_session_summary(session)
                    if summary:
                        console.print(f"[dim]• {session} - {summary['ctf_name']}")
                        if summary['challenge_name']:
                            console.print(f"    Challenge: {summary['challenge_name']}")
                        console.print(f"    Paths: {summary['paths_explored']}, Findings: {summary['findings_count']}[/dim]")
            else:
                console.print(f"[dim]No CTF sessions found[/dim]")

        elif subcommand == "status":
            current_session = self.ctf_session_manager.current_session
            if current_session:
                summary = self.ctf_session_manager.get_session_summary()
                if summary:
                    console.print(f"[cyan]Current CTF Session: {summary['session_id']}[/cyan]")
                    console.print(f"[dim]CTF: {summary['ctf_name']}[/dim]")
                    if summary['challenge_name']:
                        console.print(f"[dim]Challenge: {summary['challenge_name']}[/dim]")
                    console.print(f"[dim]Created: {summary['created_at'][:19]}[/dim]")
                    console.print(f"[dim]Paths explored: {summary['paths_explored']}[/dim]")
                    console.print(f"[dim]Findings: {summary['findings_count']}[/dim]")
            else:
                console.print(f"[dim]No active CTF session[/dim]")

        elif subcommand == "log":
            if len(parts) < 4:
                console.print(f"[red]Usage: /ctf log <reasoning|path|finding> <details>[/red]")
                return None

            log_type = parts[2]
            details = " ".join(parts[3:])

            if log_type == "reasoning":
                if self.ctf_session_manager.log_reasoning(details):
                    console.print(f"[green]Reasoning logged[/green]")
                else:
                    console.print(f"[red]No active CTF session[/red]")
            elif log_type == "path":
                # Parse path details (basic parsing for now)
                path_data = {"path": details, "method": "unknown", "result": "logged", "notes": ""}
                if self.ctf_session_manager.log_path_explored(path_data):
                    console.print(f"[green]Path logged[/green]")
                else:
                    console.print(f"[red]No active CTF session[/red]")
            elif log_type == "finding":
                # Parse finding details (basic parsing for now)
                finding_data = {
                    "type": "unknown",
                    "severity": "unknown",
                    "description": details,
                    "location": "",
                    "evidence": "",
                    "remediation": ""
                }
                if self.ctf_session_manager.log_finding(finding_data):
                    console.print(f"[green]Finding logged[/green]")
                else:
                    console.print(f"[red]No active CTF session[/red]")
            else:
                console.print(f"[red]Unknown log type: {log_type}[/red]")

        return None

    def _handle_interrupt(self, signum, frame):
        self.paused = True
        console.print(f"\n[yellow]🛑 Agent paused by Ctrl+C. Provide guidance to continue.[/yellow]")
        console.print(f"[dim]Your next input will steer the agent.[/dim]")
        return "PAUSED"

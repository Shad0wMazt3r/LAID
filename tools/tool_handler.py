import json
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from .file_operations import FileOperations
from .command_executor import CommandExecutor
from .weather_service import WeatherService

console = Console()

class ToolHandler:
    def __init__(self):
        self.file_ops = FileOperations()
        self.command_executor = CommandExecutor()
        self.weather_service = WeatherService()
    
    def handle_tool_call(self, tool_call):
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        if function_name == "get_weather":
            if "location" not in arguments:
                return {"error": "Missing required parameter: location"}
            return self.weather_service.get_weather(arguments["location"])
        
        elif function_name == "execute_command":
            if "command" not in arguments:
                return {"error": "Missing required parameter: command"}
            return self.command_executor.execute_command(arguments["command"])
        
        elif function_name == "read_file":
            if "filepath" not in arguments:
                return {"error": "Missing required parameter: filepath"}
            return self.file_ops.read_file(arguments["filepath"])
        
        elif function_name == "list_files":
            if "directory" not in arguments:
                return {"error": "Missing required parameter: directory"}
            return self.file_ops.list_files(arguments["directory"])
        
        elif function_name == "write_file":
            if "filepath" not in arguments or "content" not in arguments:
                return {"error": "Missing required parameters: filepath, content"}
            return self.file_ops.write_file(arguments["filepath"], arguments["content"])
        
        elif function_name == "edit_file":
            if "filepath" not in arguments or "old_text" not in arguments or "new_text" not in arguments:
                return {"error": "Missing required parameters: filepath, old_text, new_text"}
            return self.file_ops.edit_file(arguments["filepath"], arguments["old_text"], arguments["new_text"])
        
        return {"error": f"Unknown function: {function_name}"}
    
    def display_tool_result(self, function_name, result):
        if "error" in result:
            console.print(f"[red]❌ Error: {result['error']}[/red]")
        else:
            if function_name == "read_file" and "content" in result:
                console.print()
                syntax = Syntax(result["content"][:500], "text", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title="📄 File Content", border_style="blue"))
            elif function_name == "list_files" and ("files" in result or "directories" in result):
                console.print()
                content_lines = []
                if "directories" in result:
                    for d in result["directories"]:
                        content_lines.append(f"📁 {d}/")
                if "files" in result:
                    for f in result["files"]:
                        content_lines.append(f"📄 {f}")
                files_text = "\n".join(content_lines)
                console.print(Panel(files_text, title="📂 Directory Contents", border_style="blue"))
            else:
                console.print(f"[green]✅ {result}[/green]")
import json
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from .file_operations import FileOperations
from .command_executor import CommandExecutor
from .weather_service import WeatherService
from .browser_service import BrowserService
from .cve_service import CVEService

console = Console()

class ToolHandler:
    def __init__(self):
        self.file_ops = FileOperations()
        self.command_executor = CommandExecutor()
        self.weather_service = WeatherService()
        self.browser_service = BrowserService()
        self.cve_service = CVEService()
    
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
        
        elif function_name == "change_directory":
            if "directorypath" not in arguments:
                return {"error": "Missing required parameter: directorypath"}
            return self.file_ops.change_directory(arguments["directorypath"])

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
        
        elif function_name == "open_browser":
            if "url" not in arguments:
                return {"error": "Missing required parameter: url"}
            return self.browser_service.open_browser(arguments["url"])
        
        elif function_name == "search":
            if "query" not in arguments:
                return {"error": "Missing required parameter: query"}
            return self.browser_service.search(arguments["query"])
        
        elif function_name == "search_cve":
            if "cve_id" not in arguments:
                return {"error": "Missing required parameter: cve_id"}
            return self.cve_service.search_cve(arguments["cve_id"])
        
        elif function_name == "search_cve_by_keyword":
            if "keyword" not in arguments:
                return {"error": "Missing required parameter: keyword"}
            return self.cve_service.search_cve_by_keyword(arguments["keyword"])
        
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
            elif function_name == "search" and "results" in result:
                console.print()
                search_text = f"Search: {result['query']}\n\n"
                for i, res in enumerate(result['results'], 1):
                    search_text += f"{i}. {res['title']}\n{res['url']}\n{res['content']}\n\n"
                console.print(Panel(search_text, title="🔍 Search Results", border_style="blue"))
            elif function_name == "search_cve" and "cve_id" in result:
                console.print()
                cve_text = f"CVE ID: {result['cve_id']}\n"
                cve_text += f"CVSS: {result.get('cvss', 'N/A')}\n"
                cve_text += f"Published: {result.get('published', 'N/A')}\n\n"
                cve_text += f"Summary:\n{result.get('summary', 'No summary available')}\n\n"
                if result.get('references'):
                    cve_text += "References:\n"
                    for ref in result['references']:
                        cve_text += f"• {ref}\n"
                console.print(Panel(cve_text, title="🛡️ CVE Information", border_style="red"))
            elif function_name == "search_cve_by_keyword" and "results" in result:
                console.print()
                keyword_text = f"Keyword: {result['keyword']}\n\n"
                for i, cve in enumerate(result['results'], 1):
                    keyword_text += f"{i}. {cve['cve_id']} (CVSS: {cve['cvss']})\n"
                    keyword_text += f"   Published: {cve['published']}\n"
                    keyword_text += f"   {cve['summary']}\n\n"
                console.print(Panel(keyword_text, title="🛡️ CVE Keyword Search", border_style="red"))
            else:
                console.print(f"[green]✅ {result}[/green]")
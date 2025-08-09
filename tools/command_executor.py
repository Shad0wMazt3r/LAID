import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

class CommandExecutor:
    @staticmethod
    def execute_command(command):
        console.print()
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
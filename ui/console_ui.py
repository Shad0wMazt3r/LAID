from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.align import Align
from rich.rule import Rule
from rich.markdown import Markdown
import colorama

colorama.init()
console = Console()

class ConsoleUI:
    @staticmethod
    def show_startup():
        console.clear()
        title = Text("🤖 LAID 🚀", style="bold magenta")
        console.print(Align.center(title))
        console.print(Align.center("[dim]Local AI-assisted Development[/dim]"))
        console.print(Rule("[blue]Ready to Chat[/blue]"))
    
    @staticmethod
    def show_tools_info():
        tools_info = """🌤️  Weather Info  📁 File Operations  🚀 Command Execution 📖 Read Files    📝 Write Files     ✏️  Edit Files
🌐 Open Browser     🔍 Web Search       🛡️ CVE Search
💬 /switch_model - Switch AI model
🎯 /mode <name> - Set agent mode (planning, log_attempts, act)
🛑 /pause or Ctrl+C - Pause agent for guidance"""
        console.print()
        console.print(Panel(tools_info, title="[cyan]Available Tools & Commands[/cyan]", border_style="cyan"))
    
    @staticmethod
    def show_current_model(model):
        console.print(f"[dim]Current Model: {model}[/dim]")
    
    @staticmethod
    def get_user_input():
        console.print()
        return Prompt.ask("[bold blue]You[/bold blue]").strip()
    
    @staticmethod
    def show_assistant_prompt():
        console.print("[bold green]Assistant:[/bold green] ", end="")
    
    @staticmethod
    def show_markdown(md_text):
        """Render markdown-formatted text in the console."""
        markdown = Markdown(md_text)
        console.print(markdown)

    @staticmethod
    def show_goodbye():
        console.print("[yellow]👋 Goodbye![/yellow]")
    
    @staticmethod
    def print_newline():
        console.print()
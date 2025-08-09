import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

class FileOperations:
    
    @staticmethod
    def change_directory(directorypath):
        try:
            os.chdir(directorypath)
            return {"success": f"Changed directory to: {directorypath}"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def read_file(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return {"content": f.read()}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def list_files(directory):
        try:
            items = os.listdir(directory)
            files = []
            directories = []
            for item in items:
                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    directories.append(item)
                else:
                    files.append(item)
            return {"files": files, "directories": directories}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def write_file(filepath, content):
        console.print()
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
            return {"error": "File write denied by user. You might want to ask the user why they denied file write."}
    
    @staticmethod
    def edit_file(filepath, old_text, new_text):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Replace", style="red")
        table.add_column("With", style="green")
        table.add_row(old_text[:50] + "...", new_text[:50] + "...")
        
        console.print()
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
            return {"error": "File edit denied by user. You might want to ask the user why they denied file write."}
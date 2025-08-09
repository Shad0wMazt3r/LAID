from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class ModelManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def switch_model(self, model_id):
        available_models = self.config_manager.get_available_models()
        available_ids = [m["id"] for m in available_models]
        if model_id in available_ids:
            self.config_manager.set_current_model(model_id)
            return True
        return False
    
    def handle_switch_model_command(self, user_input):
        parts = user_input.split()
        if len(parts) == 1:
            self._show_available_models()
            return True
        
        model_selector = parts[1]
        available_models = self.config_manager.get_available_models()
        
        try:
            model_index = int(model_selector) - 1
            if 0 <= model_index < len(available_models):
                model_id = available_models[model_index]["id"]
                if self.switch_model(model_id):
                    console.print(f"[green]✅ Switched to: {available_models[model_index]['name']}[/green]")
                    return True
        except ValueError:
            if self.switch_model(model_selector):
                model_name = next((m["name"] for m in available_models if m["id"] == model_selector), model_selector)
                console.print(f"[green]✅ Switched to: {model_name}[/green]")
                return True
        
        console.print(f"[red]❌ Model not found: {model_selector}[/red]")
        return True
    
    def _show_available_models(self):
        available_models = self.config_manager.get_available_models()
        current_model = self.config_manager.get_current_model()
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="yellow")
        table.add_column("Model Name", style="green")
        table.add_column("Model ID", style="blue")
        table.add_column("Status", style="yellow")
        
        for i, model in enumerate(available_models, 1):
            status = "✅ Current" if model["id"] == current_model else "⏸️ Available"
            table.add_row(str(i), model["name"], model["id"], status)
        
        console.print()
        console.print(Panel(table, title="🤖 Available Models", border_style="cyan"))
        console.print("[dim]Usage: /switch_model <number> or /switch_model <model_id>[/dim]")
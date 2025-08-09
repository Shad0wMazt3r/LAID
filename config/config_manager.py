import json
import os

class ConfigManager:
    def __init__(self, config_file="laid.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "lm_studio": {
                    "base_url": "http://localhost:1234/v1/",
                    "current_model": "google/gemma-3-4b"
                }
            }
    
    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def get_base_url(self):
        return self.config["lm_studio"]["base_url"]
    
    def get_current_model(self):
        return self.config["lm_studio"]["current_model"]
    
    def get_available_models(self):
        return self.config["lm_studio"].get("available_models", [])
    
    def set_current_model(self, model_id):
        self.config["lm_studio"]["current_model"] = model_id
        self.save_config()
    
    def get_system_info(self):
        return f"System: Windows, Shell: cmd.exe, Current directory: {os.getcwd()}"
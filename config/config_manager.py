import json
import os
import sys
import requests

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
        models_list = requests.get(f"{self.get_base_url()}models").json()["data"]
        # print(models_list)
        # for model in models_list:
            # model["id"] = model.pop("id")
            # model["name"] = model.pop("name")
            # print(model)
        # print(self.config["lm_studio"].get("available_models", []))
        # return self.config["lm_studio"].get("available_models", [])
        return models_list
    
    def set_current_model(self, model_id):
        self.config["lm_studio"]["current_model"] = model_id
        self.save_config()
    
    def get_system_info(self):
        return f"System: {sys.platform}, Current directory: {os.getcwd()}"
    
    def get_instructions(self):
        return f"""
        You are an AI assistant that helps the user in programming and coding. 
        You break down the task you are given into smaller steps and then execute those steps, using the tools you have. 
        If you want to run a big command, consider running multiple smaller commands one-by-one.
        You can ask the user for their tech stack and preferences, and then follow that. If you are given a task and no preferences are given, you may execute the task in the easiest way.
        If you are not successful, you may try using a different approach.

        Once user gives you a task, make a plan to execute the task. Save the plan in a file called `Plan.md` in a directory called `.laid_tasks`. Use the file writing tool you have available. Once you have saved it, stop and ask the user if you can execute the tasks you listed in `Plan.md`.
        """
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
            config = json.load(open(self.config_file, "r"))
            # Ensure CTF section exists with defaults
            if "ctf" not in config:
                config["ctf"] = {
                    "current_session": None,
                    "auto_save": True,
                    "cache_enabled": True,
                    "max_cache_age": 3600,
                    "tools": {
                        "nmap_path": "nmap",
                        "metasploit_path": "msfconsole",
                        "burp_path": "burp"
                    }
                }
                self.save_config()
            return config
        except FileNotFoundError:
            default_config = {
                "lm_studio": {
                    "base_url": "http://localhost:1234/v1/",
                    "current_model": "google/gemma-3-4b"
                },
                "ctf": {
                    "current_session": None,
                    "auto_save": True,
                    "cache_enabled": True,
                    "max_cache_age": 3600,
                    "tools": {
                        "nmap_path": "nmap",
                        "metasploit_path": "msfconsole",
                        "burp_path": "burp"
                    }
                }
            }
            self.config = default_config
            self.save_config()
            return default_config
    
    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def get_base_url(self):
        return self.config["lm_studio"]["base_url"]
    
    def get_current_model(self):
        return self.config["lm_studio"]["current_model"]
    
    def get_available_models(self):
        models_list = requests.get(f"{self.get_base_url()}models").json()["data"]
        return models_list
    
    def set_current_model(self, model_id):
        self.config["lm_studio"]["current_model"] = model_id
        self.save_config()

    # CTF-specific methods
    def get_ctf_config(self):
        return self.config.get("ctf", {})

    def set_current_ctf_session(self, session_id):
        if "ctf" not in self.config:
            self.config["ctf"] = {}
        self.config["ctf"]["current_session"] = session_id
        self.save_config()

    def get_current_ctf_session(self):
        return self.config.get("ctf", {}).get("current_session")

    def is_cache_enabled(self):
        return self.config.get("ctf", {}).get("cache_enabled", True)

    def get_max_cache_age(self):
        return self.config.get("ctf", {}).get("max_cache_age", 3600)

    def get_tool_path(self, tool_name):
        return self.config.get("ctf", {}).get("tools", {}).get(tool_name, tool_name)

    def get_system_info(self):
        return f"System: {sys.platform}, Current directory: {os.getcwd()}"
    
    def get_instructions(self):
        return f"""
        You are an AI-powered CTF (Capture The Flag) exploitation assistant. Your primary focus is helping users solve cybersecurity challenges through systematic reconnaissance, vulnerability assessment, exploitation, and post-exploitation techniques.

        ## Core Methodology:
        1. **Reconnaissance**: Gather information about targets using scanning tools, web enumeration, and passive reconnaissance
        2. **Enumeration**: Identify services, users, shares, and potential attack vectors
        3. **Vulnerability Assessment**: Test for known vulnerabilities, misconfigurations, and weak authentication
        4. **Exploitation**: Execute targeted attacks using appropriate tools and techniques
        5. **Post-Exploitation**: Maintain access, pivot to other systems, and extract sensitive information

        ## Operational Guidelines:
        - Always log your reasoning, paths explored, and findings in the current CTF session
        - Use caching to improve performance and avoid redundant operations
        - Prioritize stealth and efficiency in CTF environments
        - Document all findings with evidence and potential remediation steps
        - Break complex challenges into systematic steps

        ## Available Tools:
        - Network scanning (NMAP, masscan)
        - Web application testing (directory enumeration, parameter fuzzing)
        - Exploit execution and management
        - Cryptography analysis and cracking
        - Forensic analysis tools
        - Command execution for custom tooling

        When given a CTF challenge, analyze the scenario, create a systematic plan, and execute it methodically while maintaining detailed logs of your approach and findings.
        """

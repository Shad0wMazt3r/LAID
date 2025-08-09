from .planning import planning_prompt
from .log_attempts import log_attempts_prompt
from .act import act_prompt

class ModeManager:
    def __init__(self):
        self.current_mode = None
        self.modes = {
            "planning": planning_prompt,
            "log_attempts": log_attempts_prompt,
            "act": act_prompt
        }
    
    def set_mode(self, mode_name):
        if mode_name in self.modes:
            self.current_mode = mode_name
            return True
        return False
    
    def get_current_mode_prompt(self):
        if self.current_mode:
            return self.modes[self.current_mode]
        return ""
    
    def clear_mode(self):
        self.current_mode = None
    
    def get_available_modes(self):
        return list(self.modes.keys())
#!/usr/bin/env python3
from core.chatbot import LMStudioChatbot
from ui.console_ui import ConsoleUI

def main():
    ui = ConsoleUI()
    ui.show_startup()
    
    chatbot = LMStudioChatbot()
    ui.show_tools_info()
    ui.show_current_model(chatbot.config_manager.get_current_model())
    
    while True:
        user_input = ui.get_user_input()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            ui.show_goodbye()
            break
        
        if not user_input:
            continue
        
        ui.show_assistant_prompt()
        response = chatbot.chat_stream(user_input)
        if response:
            ui.print_newline()

if __name__ == "__main__":
    main()
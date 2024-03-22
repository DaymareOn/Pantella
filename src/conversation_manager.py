from src.logging import logging
import os
import importlib
import json

Manager_Types = {}
# Get all Managers from src/conversation_managers/ and add them to Manager_Types
for file in os.listdir(os.path.join(os.path.dirname(__file__), "conversation_managers/")):
    if file.endswith(".py") and not file.startswith("__"):
        module_name = file[:-3]
        if module_name != "base_conversation_manager":
            module = importlib.import_module(f"src.conversation_managers.{module_name}")
            Manager_Types[module.manager_slug] = module    


# Create Manager object using the config provided
    
def create_manager(config):
    if config.conversation_manager != "auto": # if a specific conversation manager is specified
        if config.conversation_manager not in Manager_Types:
            logging.error(f"Could not find conversation manager: {config.conversation_manager}! Please check your config.json file and try again!")
            input("Press enter to continue...")
            raise ValueError(f"Could not find conversation manager: {config.conversation_manager}! Please check your config.json file and try again!")
        module = Manager_Types[config.conversation_manager]
        if config.game_id not in module.valid_games:
            logging.error(f"Game '{config.game_id}' not supported by conversation manager {module.manager_slug}")
            input("Press enter to continue...")
            raise ValueError(f"Game '{config.game_id}' not supported by conversation manager {module.manager_slug}")
        manager = module.ConversationManager(config)
        return manager
    else: # if no specific conversation manager is specified
        game_config = config.game_configs[config.game_id]
        module = Manager_Types[game_config['conversation_manager']]
        manager = module.ConversationManager(config)
        return manager
import logging
import src.behaviors.base_behavior as base_behavior

class Follow(base_behavior.BaseBehavior):
    def __init__(self, manager):
        super().__init__(manager)
        self.keyword = "offended"
    
    def run(self):
        logging.info(f"The player offended the NPC")
        self.manager.conversation_manager.game_state_manager.write_game_info('_mantella_aggro', '1')
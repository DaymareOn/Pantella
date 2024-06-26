from src.logging import logging
import src.behaviors.base_behavior as base_behavior

class strip(base_behavior.BaseBehavior):
    def __init__(self, manager):
        super().__init__(manager)
        self.keyword = "Strip"
        self.description = "If {perspective_player_name} wants you to take off all your clothes, and you're comfortable and willing to do so, begin your response with 'Strip:'."
        self.example = "'Take off your clothes.' 'Strip: Okay, here goes.'"
        self.valid_games = ["skyrim","skyrimvr"]
    
    def run(self, speaker_character=None, sentence=None):
        logging.info(f"{speaker_character.name} is stripping all their clothes off.")
        self.new_game_event(f"{speaker_character.name} stripped all their clothes off and is now completely naked.")
        self.queue_actor_method(speaker_character,"Wait","2")
        self.queue_actor_method(speaker_character,"TakeEverythingOff")

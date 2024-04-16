print("Importing game_interfaces/creation_engine_file_buffers.py")
from src.logging import logging, time
from src.game_interfaces.base_interface import BaseGameInterface
import src.utils as utils
import os
logging.info("Imported required libraries in game_interfaces/creation_engine_file_buffers.py")

valid_games = ["fallout4","skyrim","fallout4vr","skyrimvr"]
interface_slug = "creation_engine_file_buffers"

class GameInterface(BaseGameInterface):
    def __init__(self,conversation_manager):
        super().__init__(conversation_manager, valid_games, interface_slug)
        if not os.path.exists(f"{self.config.game_path}"):
            self.ready = False
            logging.error(f"Game path does not exist: {self.config.game_path}")
        else:
            if not os.path.exists(self.config.game_path+'/_mantella_skyrim_folder.txt'):
                logging.warn(f'''Warning: Could not find _mantella_skyrim_folder.txt in {self.config.game_path}.\nIf you have not yet casted the Mantella spell in-game you can safely ignore this message.\nIf you have casted the Mantella spell please check that your\nMantellaSoftware/config.json "skyrim_folder" has been set correctly\n(instructions on how to set this up are in the config file itself).\nIf you are still having issues, a list of solutions can be found here: \nhttps://github.com/art-from-the-machine/Mantella#issues-qa\n''')
        if not os.path.exists(self.mod_voice_dir):
            raise FileNotFoundError(f"Mod voice directory not found at {self.mod_voice_dir}")
        self.prev_game_time = ''
        logging.info("Loading creation engine file buffers game interface")

    @property
    def game_path(self):
        return self.config.game_path
    
    @property
    def mod_path(self):
        return self.config.mod_path
    
    @property
    def mod_voice_dir(self):
        return self.mod_path + "\\Sound\\Voice\\Mantella.esp"

    def write_game_info(self, text_file_name, text):
        max_attempts = 2
        delay_between_attempts = 5

        for attempt in range(max_attempts):
            try:
                with open(f'{self.game_path}/{text_file_name}.txt', 'w', encoding='utf-8') as f:
                    f.write(text)
                break
            except PermissionError:
                logging.info(f'Permission denied to write to {text_file_name}.txt. Retrying...')
                if attempt + 1 == max_attempts:
                    raise
                else:
                    time.sleep(delay_between_attempts)
        return None


    def load_data_when_available(self, text_file_name, text = '', callback = None):
        while text == '':
            try:
                with open(f'{self.game_path}/{text_file_name}.txt', 'r', encoding='utf-8') as f:
                    text = f.readline().strip()
            except:
                with open(f'{self.game_path}/{text_file_name}.txt', 'r', encoding='ansi') as f:
                    text = f.readline().strip()
            # decrease stress on CPU while waiting for file to populate
            if callback != None:
                callback()
            time.sleep(0.01)
        return text
    

    @utils.time_it
    def reset_game_info(self):
        self.write_game_info('_mantella_current_actor', '')
        self.write_game_info('_mantella_actor_methods', '')

        self.write_game_info('_mantella_current_actor_ref_id', '')
        self.write_game_info('_mantella_current_actor_base_id', '')

        self.write_game_info('_mantella_current_location', '')

        self.write_game_info('_mantella_in_game_time', '')

        self.write_game_info('_mantella_active_actors', '')

        self.write_game_info('_mantella_in_game_events', '')

        self.write_game_info('_mantella_status', 'False')

        self.write_game_info('_mantella_actor_is_enemy', 'False')

        self.write_game_info('_mantella_actor_is_in_combat', 'False')

        self.write_game_info('_mantella_actor_relationship', '')

        self.write_game_info('_mantella_character_selection', 'True')

        self.write_game_info('_mantella_say_line', 'False')
        self.write_game_info('_mantella_say_line_2', 'False')
        self.write_game_info('_mantella_say_line_3', 'False')
        self.write_game_info('_mantella_say_line_4', 'False')
        self.write_game_info('_mantella_say_line_5', 'False')
        self.write_game_info('_mantella_say_line_6', 'False')
        self.write_game_info('_mantella_say_line_7', 'False')
        self.write_game_info('_mantella_say_line_8', 'False')
        self.write_game_info('_mantella_say_line_9', 'False')
        self.write_game_info('_mantella_say_line_10', 'False')
        self.write_game_info('_mantella_actor_count', '0')
        if not os.path.exists(f'{self.game_path}/_mantella_context_string.txt'):
            self.write_game_info('_mantella_context_string', '')

        self.write_game_info('_mantella_player_input', '')

        self.write_game_info('_mantella_actor_methods', '')

        self.write_game_info('_mantella_radiant_dialogue', 'False')
    
    
    def write_dummy_game_info(self, character_name):
        """Write fake data to game files when debugging"""

        self.write_game_info('_mantella_current_actor', character_name)

        character_id = '0'
        self.write_game_info('_mantella_current_actor_ref_id', character_id)
        self.write_game_info('_mantella_current_actor_base_id', character_id)

        location = 'Skyrim'
        self.write_game_info('_mantella_current_location', location)
        
        in_game_time = '07/12/0210 10:31'
        self.write_game_info('_mantella_in_game_time', in_game_time)

        return character_name, character_id, location, in_game_time
    

    def load_character(self):
        """Wait for character ID to populate then load character name"""
        
        character_base_id = self.load_data_when_available('_mantella_current_actor_base_id', '')
        character_ref_id = self.load_data_when_available('_mantella_current_actor_ref_id', '')
        if (character_base_id == '0' and character_ref_id == '0') or (character_base_id == '' and character_ref_id == ''): # if character ID is 0 or empty, check old id file for refid
            with open(f'{self.game_path}/_mantella_current_actor_id.txt', 'r') as f:
                character_id = f.readline().strip()
            character_ref_id = character_id
            character_base_id = None # No base ID available
        time.sleep(0.5) # wait for file to register
        with open(f'{self.game_path}/_mantella_current_actor.txt', 'r') as f:
            character_name = f.readline().strip()
        
        return character_name, character_ref_id, character_base_id
    
    def load_player_name(self):
        """Wait for player name to populate"""

        player_name = self.load_data_when_available('_mantella_player_name', '')
        return player_name
    
    def load_player_race(self):
        """Wait for player race to populate"""
        
        player_race = self.load_data_when_available('_mantella_player_race', '')
        player_race = player_race[0].upper() + player_race[1:].lower()
        return player_race
    
    def load_player_gender(self):
        """Wait for player gender to populate"""
        
        player_gender = self.load_data_when_available('_mantella_player_gender', '')
        return player_gender
    
    def get_current_context_string(self):
        """Wait for context string to populate"""
        
        with open(f'{self.game_path}/_mantella_context_string.txt', 'r', encoding='utf-8') as f:
            context_string = f.readline().strip()
        return context_string
    
    def queue_actor_method(self, actor_character, method_name, *args):
        """Queue an arbitrary method to be run on the actor in game via the game interface."""
        logging.info(f'Calling {method_name} on {actor_character.name}...')
        # string_id = actor_character.ref_id
        # if len(string_id) < 8:
        #     string_id = '0'*(8-len(string_id)) + string_id # pad string_id with leading zeros if it's less than 8 characters long
        # string_int = int(string_id, 16) # convert string_id from string hex to int hex
        function_call = f"{str(actor_character.refid_int)}|{method_name}"
        if len(args) > 0:
            function_call += '|'
            for arg in args:
                function_call += f'{arg}<>'
            if function_call.endswith('<>'):
                function_call = function_call[:-2]
        max_attempts = 2
        delay_between_attempts = 1
        for attempt in range(max_attempts):
            try:
                with open(f'{self.game_path}/_mantella_actor_methods.txt', 'a', encoding='utf-8') as f:
                    f.write(f'{function_call}\n')
                break
            except PermissionError:
                logging.info(f'Permission denied to write to _mantella_actor_methods.txt. Retrying...')
                if attempt + 1 == max_attempts:
                    raise
                else:
                    time.sleep(delay_between_attempts)

    def is_radiant_dialogue(self):
        with open(f'{self.game_path}/_mantella_radiant_dialogue.txt', 'r', encoding='utf-8') as f: # check if radiant dialogue is enabled
            radiant_dialogue = f.readline().strip().lower()
        return radiant_dialogue == 'true'

    def is_conversation_ended(self):
        with open(f'{self.game_path}/_mantella_end_conversation.txt', 'r', encoding='utf-8') as f: # check if conversation has ended
            conversation_ended = f.readline().strip().lower()
        return conversation_ended == 'true'
    
    def load_ingame_actor_count(self):
        with open(f'{self.game_path}/_mantella_actor_count.txt', 'r', encoding='utf-8') as f: # check how many characters are in the conversation
            try:
                num_characters_selected = int(f.readline().strip())
            except:
                logging.info('Failed to read _mantella_actor_count.txt')
                num_characters_selected = 0
        return num_characters_selected
    
    def debugging_setup(self, debug_character_name):
        """Select character based on debugging parameters"""

        # None == in-game character chosen by spell
        if debug_character_name == 'None':
            character_name, character_ref_id, character_base_id = self.load_character()
        else:
            character_name = debug_character_name
            debug_character_name = ''

        player_name = self.load_player_name()
        player_race = self.load_player_race()
        player_gender = self.load_player_gender()
        radiant_dialogue = self.is_radiant_dialogue() # get the radiant dialogue setting from _mantella_radiant_dialogue.txt

        character_name, character_ref_id, character_base_id, location, in_game_time = self.write_dummy_game_info(character_name)

        return character_name, character_ref_id, character_base_id, location, in_game_time, player_name, player_race, player_gender, radiant_dialogue
    
    
    def load_unnamed_npc(self, character_name):
        """Load generic NPC if character cannot be found in character database"""

        male_voice_models = self.conversation_manager.character_database.male_voice_models
        female_voice_models = self.conversation_manager.character_database.female_voice_models
        voice_model_ids = self.conversation_manager.character_database.voice_model_ids

        actor_voice_model = self.load_data_when_available('_mantella_actor_voice', '')
        actor_voice_model_id = actor_voice_model.split('(')[1].split(')')[0]
        actor_voice_model_name = actor_voice_model.split('<')[1].split(' ')[0]

        actor_race = self.load_data_when_available('_mantella_actor_race', '')
        actor_race = actor_race.split('<')[1].split(' ')[0]

        actor_sex = self.load_data_when_available('_mantella_actor_sex', '')

        voice_model = ''
        for key in voice_model_ids:
            # using endswith because sometimes leading zeros are ignored
            if actor_voice_model_id.endswith(key):
                voice_model = voice_model_ids[key]
                break
        
        # if voice_model not found in the voice model ID list
        if voice_model == '':
            voice_model = self.conversation_manager.character_database.get_character_by_voice_folder(actor_voice_model_name)["voice_model"] # return voice model from actor_voice_model_name
        else:    
            if actor_sex == '1':
                try:
                    # voice_model = random.choice(female_voice_models[actor_race]) # Get random voice model from list of generic female voice models
                    # TODO: Enable this after adding random name generation to generic NPCs, otherwise all generic NPCs will share the same info I think
                    voice_model = female_voice_models[actor_race+ "Race"][0] # Default to the first for now, change later
                except:
                    voice_model = 'Female '+actor_race # Default to Same Sex Racial Equivalent
            else:
                try: 
                    # voice_model = random.choice(male_voice_models[actor_race]) # Get random voice model from list of generic male voice models
                    # TODO: Enable this after adding random name generation to generic NPCs, otherwise all generic NPCs will share the same info I think
                    voice_model = male_voice_models[actor_race+ "Race"][0] # Default to the first for now, change later
                except:
                    voice_model = 'Male '+actor_race # Default to Same Sex Racial Equivalent

        skyrim_voice_folder = self.conversation_manager.character_database.get_voice_folder_by_voice_model(voice_model)
        
        character_info = {
            'name': character_name, # TODO: Generate random names for generic NPCs and figure out how to apply them in-game
            'bio': f'{character_name} is a {actor_race} {"Woman" if actor_sex=="1" else "Man"}.', # TODO: Generate more detailed background for generic NPCs
            'voice_model': voice_model,
            'skyrim_voice_folder': skyrim_voice_folder[0], # Default to the first for now, maybe change later?
        }

        # TODO: Enable this after adding random name generation to generic NPCs, otherwise all generic NPCs will share the same info I think
        # (Example: All Bandits would see themselves as Male Nord Bandits if the first Bandit you talked to was a Male Nord Bandit)
        # character_database.patch_character_info(character_info) # Add character info to skyrim_characters json directory if using json mode

        return character_info
    
    def get_current_location(self, presume = ''):
        """Return the current location"""
        location = self.load_data_when_available('_mantella_current_location', presume)
        if location.lower() == 'none' or location == "": # location returns none when out in the wild
            location = 'Skyrim'
        return location
    
    def get_current_game_time(self):
        """Return the current in-game time"""
        in_game_time = self.load_data_when_available('_mantella_in_game_time', '') # Example: 07/12/0713 10:31
        in_game_chunks = in_game_time.split(' ')
        
        date = in_game_chunks[0] # Example: 07/12/0713
        date_chunks = date.split('/')
        month = int(date_chunks[0])
        day = int(date_chunks[1])
        year = int(date_chunks[2])

        time24 = in_game_chunks[1] # Example: 10:31
        time_chunks = time24.split(':')
        hour24 = int(time_chunks[0]) # 24 hour time
        hour12 = hour24 if hour24 <= 12 else hour24 - 12 # 12 hour time
        ampm = 'AM' if hour24 < 12 else 'PM' # AM or PM
        minute = int(time_chunks[1])
        time12 = f'{hour12}:{minute:02} {ampm}' # Example: 10:31 AM

        
        return {
            'year': year, # The current year in-game
            'month': month, # The current month in-game
            'day': day, # The current day in-game
            'hour24': hour24, # The current hour in-game in 24 hour time
            'hour12': hour12, # The current hour in-game in 12 hour time
            'minute': minute, # The current minute in-game
            'time24': time24, # The current time in-game in 24 hour time format (Example: 13:31)
            'time12': time12, # The current time in-game in 12 hour time format (Example: 1:31 PM)
            'ampm': ampm, # AM or PM
        }
    
    def get_dummy_game_time(self):
        """Return a dummy in-game time for debugging"""
        return {
            'year': 0,
            'month': 0,
            'day': 0,
            'hour24': 0,
            'hour12': 0,
            'minute': 0,
            'time24': '00:00',
            'time12': '00:00 AM',
            'ampm': 'AM',
        }
    
    def convert_to_in_game_timestamp(self, in_game_time): # Takes an in_game_time object(like what get_current_game_time() returns) and converts it to the number of minutes since midnight at 00:00 01/01/0000
        """Convert an in_game_time object to the number of minutes since midnight at 00:00 01/01/0000"""
        minutes_since_midnight = in_game_time['hour24'] * 60 + in_game_time['minute']
        days_since_0000 = (in_game_time['year'] * 365) + (in_game_time['month'] * 30) + in_game_time['day']
        return days_since_0000 * 1440 + minutes_since_midnight
    
    def time_between_string(self, start_time, end_time):
        """Calculate the time between two in-game timestamps and return a string describing the time between them"""
        start_time = self.convert_to_in_game_timestamp(start_time)
        end_time = self.convert_to_in_game_timestamp(end_time)
        time_between = end_time - start_time
        time_between_string = "" # Example: 2 years, 3 months, 2 days, 4 hours and 5 minutes
        if time_between >= 525600:
            years = int(time_between / 525600)
            time_between_string += f'{years} year{"s" if years > 1 else ""}, '
            time_between -= years * 525600
        if time_between >= 43200:
            months = int(time_between / 43200)
            time_between_string += f'{months} month{"s" if months > 1 else ""}, '
            time_between -= months * 43200
        if time_between >= 1440:
            days = int(time_between / 1440)
            time_between_string += f'{days} day{"s" if days > 1 else ""}, '
            time_between -= days * 1440
        if time_between >= 60:
            hours = int(time_between / 60)
            time_between_string += f'{hours} hour{"s" if hours > 1 else ""}, '
            time_between -= hours * 60
        if time_between > 0:
            minutes = int(time_between)
            time_between_string += f'{minutes} minute{"s" if minutes > 1 else ""}'
        return time_between_string
        
    
    @utils.time_it
    def load_game_state(self):
        """Load game variables from _mantella_ files in Skyrim folder (data passed by the Mantella spell)"""

        if self.conversation_manager.config.debug_mode == '1':
            character_name, character_ref_id, character_base_id, location, in_game_time, player_name, player_race, player_gender = self.debugging_setup(self.conversation_manager.config.debug_character_name)
        else:
            location = self.get_current_location()
            in_game_time = self.get_current_game_time()
            character_name, character_ref_id, character_base_id = self.load_character() # get the character's name and id from _mantella_current_actor.txt and _mantella_current_actor_id.txt
            player_name = self.load_player_name() # get the player's name from _mantella_player_name.txt
            player_race = self.load_player_race() # get the player's race from _mantella_player_race.txt
            player_gender = self.load_player_gender() # get player's gender from _mantella_player_gender.txt
            radiant_dialogue = self.is_radiant_dialogue() # get the radiant dialogue setting from _mantella_radiant_dialogue.txt    
            # tell Skyrim papyrus script to start waiting for voiceline input
            self.write_game_info('_mantella_end_conversation', 'False')        
        
        character_info, is_generic_npc = self.conversation_manager.character_database.get_character(character_name, character_ref_id, character_base_id) # get character info from character database
        # TODO: Improve character lookup to be more accurate and to include generating character stats inspired by their generic name for generic NPCs instead of leaving them generic.
        # (example: make a backstory for a Bandit because the NPC was named Bandit, then generate a real name, and background inspired by that vague name for use in-corversation)
        # try: # load character from skyrim_characters json directory 
        #     character_info = self.conversation_manager.character_database.named_index[character_name]
        #     logging.info(f"Found {character_name} in character database as a named NPC: {character_info['name']}")
        #     is_generic_npc = False
        # except KeyError: # character not found
        #     try: # try searching by ID
        #         logging.info(f"Could not find {character_name} in character database. Searching by ID {character_id}...")
        #         character_info = self.conversation_manager.character_database.baseid_int_index[character_id]
        #         is_generic_npc = False
        #     except KeyError:
        #         logging.info(f"NPC '{character_name}' could not be found in character database. If this is not a generic NPC, please ensure '{character_name}' exists in the CSV's 'name' column exactly as written here, and that there is a voice model associated with them.")
        #         character_info = self.load_unnamed_npc(character_name)
        #         is_generic_npc = True

        location = self.get_current_location(location) # Check if location has changed since last check

        in_game_time = self.get_current_game_time() # Check if in-game time has changed since last check

        actor_voice_model = self.load_data_when_available('_mantella_actor_voice', '')
        actor_voice_model_name = actor_voice_model.split('<')[1].split(' ')[0]
        character_info['in_game_voice_model'] = actor_voice_model_name
        character_info['refid_int'] = character_ref_id
        character_info['baseid_int'] = character_base_id
        character_info['character_name'] = character_name
        character_info['in_game_voice_model_id'] = actor_voice_model.split('(')[1].split(')')[0]

        actor_relationship_rank = self.load_data_when_available('_mantella_actor_relationship', '')
        try:
            actor_relationship_rank = int(actor_relationship_rank)
        except:
            actor_relationship_rank = 0
        character_info['in_game_relationship_level'] = actor_relationship_rank

        return character_info, location, in_game_time, is_generic_npc, player_name, player_race, player_gender, radiant_dialogue
    

    def new_time(self, in_game_time=None):
        """Check if the in-game time has changed since the last check"""
        if in_game_time == None:
            in_game_time = self.get_current_game_time()
        if in_game_time['hour24'] != self.prev_game_time:
            self.prev_game_time = in_game_time['hour24']
            return True
        return False
    
    @utils.time_it
    def update_game_events(self):
        """Add in-game events to player's response"""

        # append in-game events to player's response
        with open(f'{self.game_path}/_mantella_in_game_events.txt', 'r', encoding='utf-8') as f:
            in_game_events_lines = f.readlines()[-5:] # read latest 5 events

        # encapsulate events in {}
        formatted_in_game_events_lines = ['*{}*'.format(line.strip()) for line in in_game_events_lines]
        in_game_events = '\n'.join(formatted_in_game_events_lines)

        # Is Player in combat with NPC
        in_combat = self.load_data_when_available('_mantella_actor_is_enemy', '').lower() == 'true' 
        character = self.conversation_manager.chat_manager.active_character
        perspective_name, trust = character.get_perspective_player_identity()
        if in_combat:
            in_game_events = in_game_events + f'\n*{perspective_name} is fighting {character.name}. This is either because they are enemies or because {perspective_name} attacked {character.name} first.*'

        if len(in_game_events) > 0:
            logging.info(f'In-game events since previous exchange:\n{in_game_events}')

        # once the events are shared with the NPC, clear the file
        self.write_game_info('_mantella_in_game_events', '')

        # append the time to player's response
        in_game_time = self.get_current_game_time() # Current in-game time
        print(in_game_time)
        # only pass the in-game time if it has changed by at least an hour
        if self.new_time(in_game_time):
            time_group = utils.get_time_group(in_game_time['hour24'])

            time_string = f"The time is now {in_game_time['time12']} {time_group}."
            logging.info(time_string)
            
            formatted_in_game_time = f"*{time_string}*\n"
            in_game_events = formatted_in_game_time + in_game_events
        
        if len(in_game_events.strip()) > 0:
            logging.info(f'In-game events since previous exchange:\n{in_game_events}')
            if len(self.conversation_manager.messages) == 0: # if there are no messages in the conversation yet, add in-game events to the first message from the system
                self.conversation_manager.new_message({
                    "role": self.conversation_manager.config.system_name,
                    "content": in_game_events,
                })
            else: # if there are messages in the conversation, add in-game events to the last message from the system
                last_message = self.conversation_manager.messages[-1]
                if last_message['role'] == self.conversation_manager.config.system_name: # if last message was from the system, add in-game events to the system message
                    self.conversation_manager.messages[-1]['content'] += "\n" + in_game_events
                else: # if last message was from the NPC, add in-game events to the ongoing conversation as a new message from the system
                    self.conversation_manager.new_message({
                        "role": self.conversation_manager.config.system_name,
                        "content": in_game_events,
                    }) # add in-game events to current ongoing conversation
    
    @utils.time_it
    def end_conversation(self):
        """End the conversation in-game"""
        if self.conversation_manager.character_manager.active_character_count() <= 0:
            logging.info('Conversation ended.')
            self.conversation_manager.conversation_ended = True # set conversation_ended to True to prevent the conversation from continuing
            self.conversation_manager.in_conversation = False # set in_conversation to False to allow the conversation to be restarted

            self.write_game_info('_mantella_in_game_events', '') # clear in-game events
            self.write_game_info('_mantella_end_conversation', 'True') # tell Skyrim papyrus script conversation has ended
            time.sleep(self.conversation_manager.config.end_conversation_wait_time) # wait a few seconds for everything to register
        return None
    
    def remove_from_conversation(self, character):
        """Remove a character from the conversation in-game"""
        logging.info(f'Implement: Remove {character.name} from conversation in-game without ending the whole conversation')
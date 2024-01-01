from aiohttp import ClientSession
import asyncio
import os
import wave
import logging
import time
import shutil
import src.utils as utils

import unicodedata
import re
import sys

class ChatManager:
    def __init__(self, conversation_manager, config, tokenizer):
        self.conversation_manager = conversation_manager
        self.game_state_manager = conversation_manager.game_state_manager
        self.mod_folder = config.mod_path
        self.max_response_sentences = config.max_response_sentences
        self.llm = config.llm
        self.alternative_openai_api_base = config.alternative_openai_api_base
        self.temperature = config.temperature
        self.top_p = config.top_p
        self.stop = config.stop
        self.frequency_penalty = config.frequency_penalty
        self.max_tokens = config.max_tokens
        self.language = config.language
        self.tokenizer = tokenizer
        self.add_voicelines_to_all_voice_folders = config.add_voicelines_to_all_voice_folders
        self.offended_npc_response = config.offended_npc_response
        self.forgiven_npc_response = config.forgiven_npc_response
        self.follow_npc_response = config.follow_npc_response
        self.experimental_features = config.experimental_features
        self.wait_time_buffer = config.wait_time_buffer

        self.character_num = 0
        self.active_character = None

        self.wav_file = f'MantellaDi_MantellaDialogu_00001D8B_1.wav'
        self.lip_file = f'MantellaDi_MantellaDialogu_00001D8B_1.lip'

        self.end_of_sentence_chars = ['.', '?', '!', ':', ';']
        self.end_of_sentence_chars = [unicodedata.normalize('NFKC', char) for char in self.end_of_sentence_chars]

        self.sentence_queue = asyncio.Queue()


    async def get_audio_duration(self, audio_file):
        """Check if the external software has finished playing the audio file"""

        with wave.open(audio_file, 'r') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()

        # wait `buffer` seconds longer to let processes finish running correctly
        duration = frames / float(rate) + self.wait_time_buffer
        return duration
    

    def setup_voiceline_save_location(self, in_game_voice_folder):
        """Save voice model folder to Mantella Spell if it does not already exist"""
        self.in_game_voice_model = in_game_voice_folder

        in_game_voice_folder_path = f"{self.mod_folder}/{in_game_voice_folder}/"
        if not os.path.exists(in_game_voice_folder_path):
            os.mkdir(in_game_voice_folder_path)

            # copy voicelines from one voice folder to this new voice folder
            # this step is needed for Skyrim to acknowledge the folder
            example_folder = f"{self.mod_folder}/MaleNord/"
            for file_name in os.listdir(example_folder):
                source_file_path = os.path.join(example_folder, file_name)

                if os.path.isfile(source_file_path):
                    shutil.copy(source_file_path, in_game_voice_folder_path)

            self.game_state_manager.write_game_info('_mantella_status', 'Error with Mantella.exe. Please check MantellaSoftware/logging.log')
            logging.warn("Unknown NPC detected. This NPC will be able to speak once you restart Skyrim. To learn how to add memory, a background, and a voice model of your choosing to this NPC, see here: https://github.com/art-from-the-machine/Mantella#adding-modded-npcs")
            input('\nPress any key to exit...')
            sys.exit(0)


    @utils.time_it
    def save_files_to_voice_folders(self, queue_output):
        """Save voicelines and subtitles to the correct game folders"""

        audio_file, subtitle = queue_output
        if self.add_voicelines_to_all_voice_folders == '1':
            for sub_folder in os.scandir(self.mod_folder):
                if sub_folder.is_dir():
                    shutil.copyfile(audio_file, f"{sub_folder.path}/{self.wav_file}")
                    shutil.copyfile(audio_file.replace(".wav", ".lip"), f"{sub_folder.path}/{self.lip_file}")
        else:
            shutil.copyfile(audio_file, f"{self.mod_folder}/{self.active_character.in_game_voice_model}/{self.wav_file}")
            shutil.copyfile(audio_file.replace(".wav", ".lip"), f"{self.mod_folder}/{self.active_character.in_game_voice_model}/{self.lip_file}")

        logging.info(f"{self.active_character.name} should speak")
        if self.character_num == 0:
            self.game_state_manager.write_game_info('_mantella_say_line', subtitle.strip())
        else:
            say_line_file = '_mantella_say_line_'+str(self.character_num+1)
            self.game_state_manager.write_game_info(say_line_file, subtitle.strip())

    @utils.time_it
    def remove_files_from_voice_folders(self):
        for sub_folder in os.listdir(self.mod_folder):
            try:
                os.remove(f"{self.mod_folder}/{sub_folder}/{self.wav_file}")
                os.remove(f"{self.mod_folder}/{sub_folder}/{self.lip_file}")
            except:
                continue


    async def send_audio_to_external_software(self, queue_output):
        logging.info(f"Dialogue to play: {queue_output[0]}")
        self.save_files_to_voice_folders(queue_output)
        
        
        # Remove the played audio file
        #os.remove(audio_file)

        # Remove the played audio file
        #os.remove(audio_file)

    async def send_response(self, sentence_queue, event):
        """Send response from sentence queue generated by `process_response()`"""

        while True:
            queue_output = await sentence_queue.get()
            if queue_output is None:
                logging.info('End of sentences')
                break

            # send the audio file to the external software and wait for it to finish playing
            await self.send_audio_to_external_software(queue_output)
            event.set()

            audio_duration = await self.get_audio_duration(queue_output[0])
            # wait for the audio playback to complete before getting the next file
            logging.info(f"Waiting {int(round(audio_duration,4))} seconds...")
            await asyncio.sleep(audio_duration)

    def clean_sentence(self, sentence):
        def remove_as_a(sentence):
            """Remove 'As an XYZ,' from beginning of sentence"""
            if sentence.startswith('As a'):
                if ', ' in sentence:
                    logging.info(f"Removed '{sentence.split(', ')[0]} from response")
                    sentence = sentence.replace(sentence.split(', ')[0]+', ', '')
            return sentence
        
        def parse_asterisks_brackets(sentence):
            if ('*' in sentence):
                # Check if sentence contains two asterisks
                asterisk_check = re.search(r"(?<!\*)\*(?!\*)[^*]*\*(?!\*)", sentence)
                if asterisk_check:
                    logging.info(f"Removed asterisks text from response: {sentence}")
                    # Remove text between two asterisks
                    sentence = re.sub(r"(?<!\*)\*(?!\*)[^*]*\*(?!\*)", "", sentence)
                else:
                    logging.info(f"Removed response containing single asterisks: {sentence}")
                    sentence = ''

            if ('(' in sentence) or (')' in sentence):
                # Check if sentence contains two brackets
                bracket_check = re.search(r"\(.*\)", sentence)
                if bracket_check:
                    logging.info(f"Removed brackets text from response: {sentence}")
                    # Remove text between brackets
                    sentence = re.sub(r"\(.*?\)", "", sentence)
                else:
                    logging.info(f"Removed response containing single bracket: {sentence}")
                    sentence = ''

            return sentence
        
        if ('Well, well, well' in sentence):
            sentence = sentence.replace('Well, well, well', 'Well well well')

        sentence = remove_as_a(sentence)
        sentence = sentence.replace('"','')
        sentence = sentence.replace('[', '(')
        sentence = sentence.replace(']', ')')
        sentence = sentence.replace('{', '(')
        sentence = sentence.replace('}', ')')
        # local models sometimes get the idea in their head to use double asterisks **like this** in sentences instead of single
        # this converts double asterisks to single so that they can be filtered out appropriately
        sentence = sentence.replace('**','*')
        sentence = parse_asterisks_brackets(sentence)

        return sentence


    async def process_response(self, player_name, config, sentence_queue, input_text, messages, synthesizer, characters, radiant_dialogue, event):
        """Stream response from LLM one sentence at a time"""

        if config.is_local: # if local, use the player_name as the role
            messages.append({"role": player_name, "content": input_text})
        else: # if remote, use the user role
            messages.append({"role": config.user_name, "content": input_text})
            
        sentence = ''
        full_reply = ''
        num_sentences = 0
        action_taken = False
        while True:
            try:
                start_time = time.time()
                # print(f"Next Line: ")
                for chunk in self.conversation_manager.llm.acreate(messages):
                    # print(chunk.model_dump_json())
                    content = chunk.choices[0].text
                    print(content, end='')
                    if content is not None:
                        sentence += content

                        if not config.is_local: # if remote, check if the response contains the word assist for some reason. Probably some OpenAI nonsense.
                            if ('assist' in content) and (num_sentences>0): # Causes problems if asking a follower if you should help someone, if they try to say something along the lines of "Yes, we should assist them." it will cut off the sentence and basically ignore the player. TODO: fix this with a more robust solution
                                logging.info(f"'assist' keyword found. Ignoring sentence which begins with: {sentence}") 
                                break

                        content_edit = unicodedata.normalize('NFKC', content) # normalize unicode characters
                        # check if content marks the end of a sentence
                        if (any(char in content_edit for char in self.end_of_sentence_chars)):
                            sentence = self.clean_sentence(sentence)

                            if len(sentence.strip()) < 3: # Is this really necessary? "Hi." is a valid sentence, but is it really worth saying? TODO: check if this is necessary
                                logging.info(f'Skipping voiceline that is too short: {sentence}')
                                break

                            logging.info(f"LLM returned sentence took {time.time() - start_time} seconds to execute")

                            if "\n" in sentence:
                                keyword_extraction = sentence.split('\n')[0]
                                # if LLM is switching character
                                if (keyword_extraction in characters.active_characters):
                                    #TODO: or (any(key.split(' ')[0] == keyword_extraction for key in characters.active_characters))
                                    logging.info(f"Switched to {keyword_extraction}")
                                    self.active_character = characters.active_characters[keyword_extraction]
                                    # characters are mapped to say_line based on order of selection
                                    # taking the order of the dictionary to find which say_line to use, but it is bad practice to use dictionaries in this way
                                    self.character_num = list(characters.active_characters.keys()).index(keyword_extraction)
                                    full_reply += sentence
                                    sentence = ''
                                    action_taken = True
                                elif keyword_extraction == 'Player':
                                    logging.info(f"Stopped LLM from speaking on behalf of the player")
                                    break
                                elif keyword_extraction.lower() == self.offended_npc_response.lower():
                                    if self.experimental_features:
                                        logging.info(f"The player offended the NPC")
                                        self.game_state_manager.write_game_info('_mantella_aggro', '1')
                                    else:
                                        logging.info(f"Experimental features disabled. Please set experimental_features = 1 in config.ini to enable the Offended feature")
                                    full_reply += sentence
                                    sentence = ''
                                    action_taken = True
                                elif keyword_extraction.lower() == self.forgiven_npc_response.lower():
                                    if self.experimental_features:
                                        logging.info(f"The player made up with the NPC")
                                        self.game_state_manager.write_game_info('_mantella_aggro', '0')
                                    else:
                                        logging.info(f"Experimental features disabled. Please set experimental_features = 1 in config.ini to enable the Forgiven feature")
                                    full_reply += sentence
                                    sentence = ''
                                    action_taken = True
                                elif keyword_extraction.lower() == self.follow_npc_response.lower():
                                    if self.experimental_features:
                                        logging.info(f"The NPC is willing to follow the player")
                                        self.game_state_manager.write_game_info('_mantella_aggro', '2')
                                    else:
                                        logging.info(f"Experimental features disabled. Please set experimental_features = 1 in config.ini to enable the Follow feature")
                                    full_reply += sentence
                                    sentence = ''
                                    action_taken = True

                            if action_taken == False:
                                # Generate the audio and return the audio file path
                                try:
                                    audio_file = synthesizer.synthesize(self.active_character.voice_model, None, ' ' + sentence + ' ')
                                except Exception as e:
                                    logging.error(f"xVASynth Error: {e}")

                                # Put the audio file path in the sentence_queue
                                await sentence_queue.put([audio_file, sentence])

                                full_reply += sentence
                                num_sentences += 1
                                sentence = ''

                                # clear the event for the next iteration
                                event.clear()
                                # wait for the event to be set before generating the next line
                                await event.wait()

                                end_conversation = self.game_state_manager.load_conversation_ended()
                                radiant_dialogue_update = self.game_state_manager.load_radiant_dialogue()
                                # stop processing LLM response if:
                                # max_response_sentences reached (and the conversation isn't radiant)
                                # conversation has switched from radiant to multi NPC (this allows the player to "interrupt" radiant dialogue and include themselves in the conversation)
                                # the conversation has ended
                                if ((num_sentences >= self.max_response_sentences) and not radiant_dialogue) or (radiant_dialogue and not radiant_dialogue_update) or end_conversation:
                                    break
                            else:
                                action_taken = False
                break
            except Exception as e:
                logging.error(f"LLM API Error: {e}")
                error_response = "I can't find the right words at the moment."
                audio_file = synthesizer.synthesize(self.active_character.voice_model, None, error_response)
                self.save_files_to_voice_folders([audio_file, error_response])
                logging.info('Retrying connection to API...')
                time.sleep(5)

        # Mark the end of the response
        await sentence_queue.put(None)

        if config.is_local:
            messages.append({"role": player_name, "content": input_text})
        else:
            messages.append({"role": "assistant", "content": full_reply})
        
        logging.info(f"Full response saved ({self.tokenizer.get_token_count(full_reply)} tokens): {full_reply}")
        return messages
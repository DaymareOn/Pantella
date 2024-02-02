import src.utils as utils
import src.tts_types.base_tts as base_tts
import logging
import sys
import os
from pathlib import Path
import requests
import io
import soundfile as sf
import numpy as np

tts_slug = "xtts"
class Synthesizer(base_tts.base_Synthesizer): # Gets token count from OpenAI's embedding API -- WARNING SLOW AS HELL -- Only use if you don't want to set up the right tokenizer for your local model or if you don't know how to do that
    def __init__(self, conversation_manager):
        super().__init__(conversation_manager)
        self.xtts_data = self.config.xtts_data
        self.xtts_base_url = self.config.xtts_base_url
        self.xtts_server_folder = self.config.xtts_server_folder
        self.synthesize_url_xtts = self.xtts_base_url + "/tts_to_audio/"
        # self.switch_model_url = self.xtts_base_url + "/switch_model"
        self.xtts_set_tts_settings = self.xtts_base_url + "/set_tts_settings/"
        self.xtts_get_speakers_list = self.xtts_base_url + "/speakers_list/"
        self.xtts_get_models_list = self.xtts_base_url + "/get_models_list/"
        self._set_tts_settings_and_test_if_serv_running()
        # self.official_model_list = ["main","v2.0.3","v2.0.2","v2.0.1","v2.0.0"]
        logging.info(f'Available models: {self.available_models()}')
        logging.info(f'Available voices: {self.voices()}')
    
    def convert_to_16bit(self, input_file, output_file=None):
        if output_file is None:
            output_file = input_file
        # Read the audio file
        data, samplerate = sf.read(input_file)

        # Directly convert to 16-bit if data is in float format and assumed to be in the -1.0 to 1.0 range
        if np.issubdtype(data.dtype, np.floating):
            # Ensure no value exceeds the -1.0 to 1.0 range before conversion (optional, based on your data's characteristics)
            # data = np.clip(data, -1.0, 1.0)  # Uncomment if needed
            data_16bit = np.int16(data * 32767)
        elif not np.issubdtype(data.dtype, np.int16):
            # If data is not floating-point or int16, consider logging or handling this case explicitly
            # For simplicity, this example just converts to int16 without scaling
            data_16bit = data.astype(np.int16)
        else:
            # If data is already int16, no conversion is necessary
            data_16bit = data

        # Write the 16-bit audio data back to a file
        sf.write(output_file, data_16bit, samplerate, subtype='PCM_16')

    def voices(self):
        """Return a list of available voices"""
        # Code to request and return the list of available models
        response = requests.get(self.xtts_get_speakers_list)
        return response.json() if response.status_code == 200 else []
    
    def available_models(self):
        """Return a list of available models"""
        # Code to request and return the list of available models
        response = requests.get(self.xtts_get_models_list)
        return response.json() if response.status_code == 200 else []
    
    def _set_tts_settings_and_test_if_serv_running(self):
        """Set the TTS settings and test if the server is running"""
        try:
            # Sending a POST request to the API endpoint
            logging.info(f'Attempting to connect to xTTS...')
            response = requests.post(self.xtts_set_tts_settings, json=self.xtts_data)
            response.raise_for_status() 
        except requests.exceptions.RequestException as e:
            # Log the error
            logging.error(f'Could not reach the API at "{self.xtts_set_tts_settings}". Error: {e}')
            # Wait for user input before exiting
            logging.error(f'You should run xTTS api server before running Mantella.')
            input('\nPress any key to stop Mantella...')
            sys.exit(0)

    @utils.time_it
    def change_voice(self, character):
        logging.info(f'Changing voice to {character.voice_model}...') 
        logging.info(f'(Redundant Method, xTTS does not support changing voice models as all voices are calculated at runtime)')
          
    @utils.time_it
    def _synthesize_line_xtts(self, line, save_path, character, aggro=0):
        voice_path = f"{character.voice_model.replace(' ', '')}"
        data = {
            'text': line,
            'speaker_wav': voice_path,
            'language': character.language
        }       
        response = requests.post(self.synthesize_url_xtts, json=data)
        if response.status_code == 200: # if the request was successful, write the wav file to disk at the specified path
            self.convert_to_16bit(io.BytesIO(response.content), save_path)
        else:
            logging.error(f'xTTS failed to generate voiceline at: {Path(save_path)}')
            raise FileNotFoundError()
          
    def synthesize(self, character, voiceline, aggro=0):
        logging.info(f'Synthesizing voiceline: {voiceline}')
        self.change_voice(character)
        # make voice model folder if it doesn't already exist
        if not os.path.exists(f"{self.output_path}/voicelines/{character.voice_model}"):
            os.makedirs(f"{self.output_path}/voicelines/{character.voice_model}")

        final_voiceline_file_name = 'voiceline'
        final_voiceline_file =  f"{self.output_path}/voicelines/{character.voice_model}/{final_voiceline_file_name}.wav"

        try:
            if os.path.exists(final_voiceline_file):
                os.remove(final_voiceline_file)
            if os.path.exists(final_voiceline_file.replace(".wav", ".lip")):
                os.remove(final_voiceline_file.replace(".wav", ".lip"))
        except:
            logging.warning("Failed to remove spoken voicelines")

        # Synthesize voicelines
        self._synthesize_line_xtts(voiceline, final_voiceline_file, character, aggro)

        if not os.path.exists(final_voiceline_file):
            logging.error(f'xTTS failed to generate voiceline at: {Path(final_voiceline_file)}')
            raise FileNotFoundError()

        self.lip_gen(voiceline, final_voiceline_file)
        self.debug(final_voiceline_file)

        return final_voiceline_file
    
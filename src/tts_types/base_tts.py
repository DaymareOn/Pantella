
import logging
import src.utils as utils
import subprocess
import winsound
import os
from pathlib import Path

class VoiceModelNotFound(Exception):
    pass

tts_slug = "base_Synthesizer"
class base_Synthesizer:
    def __init__(self, conversation_manager):
        self.conversation_manager = conversation_manager
        self.config = self.conversation_manager.config
        # determines whether the voiceline should play internally
        self.debug_mode = self.config.debug_mode
        self.play_audio_from_script = self.config.play_audio_from_script
        # currrent game running
        self.game = self.config.game_id
        # output wav / lip files path
        self.output_path = utils.resolve_path('data')+'/data'
        # last active voice model
        self.language = self.config.language
    
    def voices(self):
        logging.info("Warning: Using voice() method of base_tts.py, this means you haven't implemented the voices() method in your new tts type. This method should return a list of available voices models for the current game from the tts.")
        input("Press enter to continue...")
        exit(0)
        return []

    @utils.time_it
    def change_voice(self, character):
        logging.info(f'Warning: Using change_voice() method of base_tts.py, this means you haven\'t implemented the change_voice() method in your new tts type. This method should change the voice of the tts to the voice model specified in the character object.')
        logging.info(f'Changing voice to: {character.voice_model}')
        logging.info('Voice model not loaded, please fix your code.')
        input("Press enter to continue...")
        exit(0)
        return None

    @utils.time_it
    def synthesize(self, text, character, **kwargs):
        logging.info(f'Warning: Using synthesizer() method of base_tts.py, this means you haven\'t implemented the synthesizer() method in your new tts type. This method should synthesize the text passed as a parameter with the voice model specified in the character object.')
        logging.info(f'Synthesizing text: {text}')
        logging.info(f'Using voice model: {character.voice_model}')
        logging.info('Using Additional parameters: {}'.format(kwargs))
        logging.info('Wav file not saved, please fix your code.')
        logging.info('Lip file not saved, please fix your code.')
        logging.info('Voice model not loaded, please fix your code.')
        input("Press enter to continue...")
        exit(0)
        return final_voiceline_file # path to wav file
         
    def run_command(self, command):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        sp = subprocess.Popen(command, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = sp.communicate()
        stderr = stderr.decode("utf-8")

    def check_face_fx_wrapper(self):
        current_dir = os.getcwd() # get current directory
        cdf_path = f'{current_dir}/FaceFXWrapper/FonixData.cdf'
        face_wrapper_executable = f'{current_dir}/FaceFXWrapper/FaceFXWrapper.exe'
        installed = False

        logging.info(f'Checking if FonixData.cdf exists at: {cdf_path}')
        if os.path.isfile(cdf_path):
            logging.info(f'Found FonixData.cdf at: {cdf_path}')
            installed = True
        else:
            logging.error(f'Could not find FonixData.cdf in "{Path(cdf_path).parent}" required by FaceFXWrapper.')
        
        logging.info(f'Checking if FaceFXWrapper.exe exists at: {face_wrapper_executable}')
        if os.path.isfile(face_wrapper_executable):
            logging.info(f'Found FaceFXWrapper.exe at: {face_wrapper_executable}')
            installed = True
        else:
            logging.error(f'Could not find FaceFXWrapper.exe in "{Path(face_wrapper_executable).parent}" with which to create a Lip Sync file, download it from: https://github.com/Nukem9/FaceFXWrapper/releases')
            
        return installed

    def lip_gen(self, voiceline, final_voiceline_file):
        current_dir = os.getcwd() # get current directory
        cdf_path = f'{current_dir}/FaceFXWrapper/FonixData.cdf'
        face_wrapper_executable = f'{current_dir}/FaceFXWrapper/FaceFXWrapper.exe'

        if self.check_face_fx_wrapper():
            try:
                self.run_command(f'{face_wrapper_executable} "{self.game.capitalize()}" "USEnglish" "{cdf_path}" "{final_voiceline_file}" "{final_voiceline_file.replace(".wav", "_r.wav")}" "{final_voiceline_file.replace(".wav", ".lip")}" "{voiceline}"')
                # remove file created by FaceFXWrapper
                if os.path.exists(final_voiceline_file.replace(".wav", "_r.wav")):
                    os.remove(final_voiceline_file.replace(".wav", "_r.wav"))
            except:
                logging.error(f'FaceFXWrapper failed to generate lip file at: {final_voiceline_file} - Falling back to default/last lip file in Mantella-Spell')
        else:
            logging.error(f'FaceFXWrapper not installed:. Falling back to default lip file in Mantella-Spell')

    def debug(self, final_voiceline_file):
        if self.debug_mode and self.play_audio_from_script:
            winsound.PlaySound(final_voiceline_file, winsound.SND_FILENAME)
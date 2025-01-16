import pathlib
import html
import time
from extensions.KokoroTtsTexGernerationWebui.src.generate import run

from modules import shared


def input_modifier(string, state):

    shared.processing_message = "*Is recording a voice message...*"
    return string

def output_modifier(string, state):


    # Escape the string for HTML safety
    string_for_tts = html.unescape(string)
    string_for_tts = string_for_tts.replace('*', '')
    string_for_tts = string_for_tts.replace('`', '')

    with open('last_message.txt', 'w') as f:
        f.write(string_for_tts)

    # Run your custom logic to generate audio
    msg_id = run(string_for_tts)

    # Construct the correct path to the 'audio' directory
    audio_dir = pathlib.Path(__file__).parent / 'audio' / f'{msg_id}.wav'


    # Add the audio playback HTML to the output string
    string += f'<audio controls><source src="file/{audio_dir.as_posix()}" type="audio/mpeg"></audio>'

    return string

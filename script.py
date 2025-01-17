import pathlib
import html
import time
from extensions.KokoroTtsTexGernerationWebui.src.generate import run, load_voice
from extensions.KokoroTtsTexGernerationWebui.src.voices import VOICES
import gradio as gr
import time

from modules import shared

def input_modifier(string, state):

    shared.processing_message = "*Is recording a voice message...*"
    return string


def voice_update(voice):
    load_voice(voice)
    return gr.Dropdown(choices=VOICES, value=voice, label="Voice", info="Select Voice", interactive=True)

def voice_preview():
    run("This is a preview of the selected voice", preview=True)
    audio_dir = pathlib.Path(__file__).parent / 'audio' / 'preview.wav'
    audio_url = f'{audio_dir.as_posix()}?v=f{int(time.time())}'
    return f'<audio controls><source src="file/{audio_url}" type="audio/mpeg"></audio>'
   

def ui():
    info = """Select a Voice. \nThe default voice is a 50-50 mix of Bella & Sarah\nVoices starting with 'a' are American
     englisch, voices with 'b' are British englisch"""
    with gr.Accordion("Kokoro"):
        voice = gr.Dropdown(choices=VOICES, value=VOICES[0], label="Voice", info=info, interactive=True)

        preview = gr.Button("Voice preview", type="secondary")

        preview_output = gr.HTML()


    voice.change(voice_update, voice)
    preview.click(fn=voice_preview, outputs=preview_output)

    



    

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

import pathlib
import html
import time
from extensions.KokoroTtsTexGernerationWebui.src.generate import run, load_voice, set_plitting_type
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
    info_voice = """Select a Voice. \nThe default voice is a 50-50 mix of Bella & Sarah\nVoices starting with 'a' are American
     englisch, voices with 'b' are British englisch"""
    with gr.Accordion("Kokoro"):
        voice = gr.Dropdown(choices=VOICES, value=VOICES[0], label="Voice", info=info_voice, interactive=True)

        preview = gr.Button("Voice preview", type="secondary")

        preview_output = gr.HTML()

        info_splitting ="""Kokoro only supports 510 tokens. One method to split the text is by sentance (default), the otherway
        is by word up to 510 tokens. """
        spltting_method = gr.Radio(["Split by Sentance", "Split by Word"], info=info_splitting, value="Split by Sentance", label_lines=2, interactive=True)


    voice.change(voice_update, voice)
    preview.click(fn=voice_preview, outputs=preview_output)

    spltting_method.change(set_plitting_type, spltting_method)

    



    

def output_modifier(string, state):


    # Escape the string for HTML safety
    string_for_tts = html.unescape(string)
    string_for_tts = string_for_tts.replace('*', '')
    string_for_tts = string_for_tts.replace('`', '')

 
    # Run your custom logic to generate audio
    msg_id = run(string_for_tts)

    # Construct the correct path to the 'audio' directory
    audio_dir = pathlib.Path(__file__).parent / 'audio' / f'{msg_id}.wav'


    # Add the audio playback HTML to the output string
    string += f'<audio controls><source src="file/{audio_dir.as_posix()}" type="audio/mpeg"></audio>'

    return string

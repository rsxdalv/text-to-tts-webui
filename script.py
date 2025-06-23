import pathlib
import html
import time
import gradio as gr
import time
import requests

from .lib.kokoro_choices import CHOICES as kokoro_choices
from .lib.settings import *
from .lib.chatterbox import chatterbox_tts 
# from lib.kokoro_choices import CHOICES as kokoro_choices
# from lib.settings import *

params = {
    "display_name": "TTS WebUI",
    "is_tab": True,
}


def history_modifier(history):
    """
    Modifies the chat history.
    Only used in chat mode.
    """
    return history


def custom_css():
    return ""


def custom_js():
    return ""


def setup():
    pass


def kokoro_settings():
    voice = gr.Dropdown(
        choices=list(kokoro_choices.items()),
        value="af_heart",
        label="Voice",
        interactive=True,
    )
    voice.change(update_voice("hexgrad/Kokoro-82M"), voice)


def chatterbox_settings():
    chatterbox_tts()


def main_settings():
    gr.Markdown("## Main Settings")
    endpoint = gr.Textbox(
        label="Endpoint",
        value="http://localhost:7778/v1/audio/speech",
        info="Endpoint for the Kokoro TTS server",
        interactive=True,
    )

    endpoint.change(update_setting("endpoint"), endpoint)

    model = gr.Dropdown(
        choices=[
            "hexgrad/Kokoro-82M",
            "chatterbox",
        ],
        value="hexgrad/Kokoro-82M",
        label="Model",
        info="Model to use for TTS",
        interactive=True,
    )

    model.change(update_setting("model"), model)

    preview = gr.Button("Voice preview", variant="secondary")

    preview_audio = gr.Audio(
        label="Preview",
        interactive=False,
    )

    preview.click(fn=voice_preview, outputs=preview_audio)


def ui():
    gr.Markdown("# TTS WebUI Extension Settings")
    with gr.Row():
        with gr.Column():
            main_settings()

        with gr.Column(), gr.Tabs():
            with gr.Tab("Chatterbox"):
                chatterbox_settings()
            with gr.Tab("Kokoro"):
                kokoro_settings()


def generate_audio(text: str):
    response = requests.post(
        settings["endpoint"],
        json={
            "model": settings["model"],
            "voice": voice_by_model.get(settings["model"], "af_heart"),
            "speed": settings["speed"],
            "params": generation_params_by_model.get(settings["model"], {}),
            "input": text,
        },
    )
    audio = response.content

    msg_id = f"audio_{int(time.time())}.wav"
    audio_path = pathlib.Path(__file__).parent / "audio" / f"{msg_id}.wav"
    with open(audio_path, "wb") as f:
        f.write(audio)
    return msg_id


def output_modifier(string, state, is_chat=False):

    # Escape the string for HTML safety
    string_for_tts = html.unescape(string)
    string_for_tts = string_for_tts.replace("*", "")
    string_for_tts = string_for_tts.replace("`", "")

    msg_id = generate_audio(string_for_tts)
    audio_dir = pathlib.Path(__file__).parent / "audio" / f"{msg_id}.wav"
    string += f'<audio controls><source src="file/{audio_dir.as_posix()}" type="audio/mpeg"></audio>'
    return string


def voice_preview():
    msg_id = generate_audio("This is a preview of the selected voice")
    audio_dir = pathlib.Path(__file__).parent / "audio" / f"{msg_id}.wav"
    return audio_dir

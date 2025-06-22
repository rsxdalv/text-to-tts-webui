import pathlib
import html
import time
import gradio as gr
import time

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


def voice_preview():
    msg_id = generate_audio("This is a preview of the selected voice")
    audio_dir = pathlib.Path(__file__).parent / "audio" / f"{msg_id}.wav"
    audio_url = f"{audio_dir.as_posix()}?v=f{int(time.time())}"
    return f'<audio controls><source src="file/{audio_url}" type="audio/mpeg"></audio>'


def kokoro_settings():
    gr.Markdown("## Kokoro TTS Settings")

    endpoint = gr.Textbox(
        label="Endpoint",
        value="http://localhost:7778/v1/audio/speech",
        info="Endpoint for the Kokoro TTS server",
        interactive=True,
    )

    def set_endpoint(endpoint):
        global settings
        settings["endpoint"] = endpoint

        return gr.update(value=endpoint)

    endpoint.change(set_endpoint, endpoint)

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

    def set_model(model):
        global settings
        settings["model"] = model

        return gr.update(value=model)

    model.change(set_model, model)

    info_voice = """Select a Voice. \nThe default voice is a 50-50 mix of Bella & Sarah\nVoices starting with 'a' are American
     english, voices with 'b' are British english"""
    with gr.Accordion("Kokoro"):
        voice = gr.Dropdown(
            choices=[
                "af_heart",
                "af_heart2",
            ],
            value="af_heart",
            label="Voice",
            info=info_voice,
            interactive=True,
        )

        preview = gr.Button("Voice preview", type="secondary")

        preview_output = gr.HTML()

    def voice_update(voice):
        global voice_by_model
        voice_by_model["hexgrad/Kokoro-82M"] = voice
        return gr.update(value=voice)

    voice.change(voice_update, voice)
    preview.click(fn=voice_preview, outputs=preview_output)


def chatterbox_settings():
    gr.Markdown("## Chatterbox Settings")


def ui():
    gr.Markdown("# TTS WebUI Extension Settings")
    with gr.Tabs():
        with gr.Tab("Kokoro"):
            kokoro_settings()
        with gr.Tab("Chatterbox"):
            chatterbox_settings()


settings = {
    "endpoint": "http://localhost:7778/v1/audio/speech",
    "model": "hexgrad/Kokoro-82M",
    "speed": 1.0,
}

voice_by_model = {
    "hexgrad/Kokoro-82M": "af_heart",
    "chatterbox": "voices/chatterbox/Alice.wav",
}

generation_params_by_model = {
    "hexgrad/Kokoro-82M": {
    },
    "chatterbox": {
        "exaggeration": 0.5,
        "cfg_weight": 0.5,
        "temperature": 0.8,
        "dtype": "float32",
    },
}

def generate_audio(text: str):
    import requests

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

    # Run your custom logic to generate audio
    # msg_id = run(string_for_tts)
    msg_id = generate_audio(string_for_tts)

    # Construct the correct path to the 'audio' directory
    audio_dir = pathlib.Path(__file__).parent / "audio" / f"{msg_id}.wav"

    # Add the audio playback HTML to the output string
    string += f'<audio controls><source src="file/{audio_dir.as_posix()}" type="audio/mpeg"></audio>'

    return string

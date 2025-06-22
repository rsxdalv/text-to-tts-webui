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


def voice_update(voice):
    load_voice(voice)
    return gr.Dropdown(
        choices=VOICES,
        value=voice,
        label="Voice",
        info="Select Voice",
        interactive=True,
    )


def voice_preview():
    msg_id = generate_audio("This is a preview of the selected voice")
    audio_dir = pathlib.Path(__file__).parent / "audio" / f"{msg_id}.wav"
    audio_url = f"{audio_dir.as_posix()}?v=f{int(time.time())}"
    return f'<audio controls><source src="file/{audio_url}" type="audio/mpeg"></audio>'


def ui():
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

        info_splitting = """Kokoro only supports 510 tokens. One method to split the text is by sentence (default), the otherway
        is by word up to 510 tokens. """
        spltting_method = gr.Radio(
            ["Split by sentence", "Split by Word"],
            info=info_splitting,
            value="Split by sentence",
            label_lines=2,
            interactive=True,
        )

    voice.change(voice_update, voice)
    preview.click(fn=voice_preview, outputs=preview_output)

    # spltting_method.change(set_plitting_type, spltting_method)


def generate_audio(text: str):
    import requests

    response = requests.post(
        "http://localhost:7778/v1/audio/speech",
        json={
            "model": "hexgrad/Kokoro-82M",
            # "input": "Hello world with custom parameters.",
            "input": text,
            "voice": "af_heart",
            "speed": 1.0,
            "params": {
                "pitch_up_key": "2",
                "index_path": "CaitArcane/added_IVF65_Flat_nprobe_1_CaitArcane_v2",
            },
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

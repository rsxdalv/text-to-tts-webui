import gradio as gr
import requests

from .settings import (
    update_generation_params,
    update_voice,
    settings,
    generation_params_by_model,
)


def chatterbox_tts():
    with gr.Column():
        # with gr.Row():
        #     voice_dropdown = gr.Dropdown(
        #         label="Saved voices", choices=["refresh to load the voices"]
        #     )
        #     # OpenFolderButton(
        #     #     get_path_from_root("voices", "chatterbox"),
        #     #     api_name="chatterbox_open_voices_dir",
        #     # )

        # audio_prompt_path = gr.Audio(
        #     label="Reference Audio", type="filepath", value=None
        # )

        # voice_dropdown.change(
        #     lambda x: gr.Audio(value=x),
        #     inputs=[voice_dropdown],
        #     outputs=[audio_prompt_path],
        # )
        with gr.Row():
            voice = gr.Dropdown(
                choices=[
                    ("Alice", "voices/chatterbox/Alice.wav"),
                    ("Emmett", "voices/chatterbox/Emmett.wav"),
                    ("Sloane", "voices/chatterbox/Sloane.wav"),
                ],
                value="voices/chatterbox/Alice.wav",
                label="Voice",
                interactive=True,
            )
            voice.change(update_voice("chatterbox"), voice)

            def get_voices():
                voices_endpoint = settings["endpoint"].replace(
                    "/v1/audio/speech", "/v1/audio/voices/chatterbox"
                )
                voices = requests.get(voices_endpoint).json()
                voices = [
                    (voice["label"], voice["value"]) for voice in voices["voices"]
                ]
                return gr.Dropdown(choices=voices, value=voices[0][1])

            button = gr.Button("Refresh", scale=0)
            button.click(get_voices, outputs=[voice])

        exaggeration = gr.Slider(
            label="Exaggeration (Neutral = 0.5, extreme values can be unstable)",
            minimum=0,
            maximum=2,
            value=0.5,
        )
        cfg_weight = gr.Slider(
            label="CFG Weight/Pace", minimum=0.0, maximum=1, value=0.5
        )
        temperature = gr.Slider(label="Temperature", minimum=0.05, maximum=5, value=0.8)

        # seed, randomize_seed_callback = randomize_seed_ui()

    with gr.Column():

        gr.Markdown("## Settings")

        with gr.Accordion("Chunking", open=True), gr.Group():
            chunked = gr.Checkbox(label="Split prompt into chunks", value=True)
            with gr.Row():
                desired_length = gr.Slider(
                    label="Desired length (characters)",
                    minimum=10,
                    maximum=1000,
                    value=200,
                    step=1,
                )
                max_length = gr.Slider(
                    label="Max length (characters)",
                    minimum=10,
                    maximum=1000,
                    value=300,
                    step=1,
                )
                halve_first_chunk = gr.Checkbox(
                    label="Halve first chunk size",
                    value=True,
                )
                cache_voice = gr.Checkbox(
                    label="Cache voice (not implemented)",
                    value=False,
                    visible=False,
                )
        # model
        with gr.Accordion("Model", open=False):
            with gr.Row():
                device = gr.Radio(
                    label="Device",
                    choices=["auto", "cuda", "mps", "cpu"],
                    value="auto",
                )
                dtype = gr.Radio(
                    label="Dtype",
                    choices=["float32", "float16", "bfloat16"],
                    value="float32",
                )
                cpu_offload = gr.Checkbox(label="CPU Offload", value=False)
                model_name = gr.Dropdown(
                    label="Model",
                    choices=["just_a_placeholder"],
                    value="just_a_placeholder",
                    visible=False,
                )

            gr.Markdown("## Optimization")
            gr.Markdown(
                """
                        By reducing cache length, the model becomes faster, but maximum generation length is reduced. Gives an error if too low.
                        For fastest speeds, reduce prompt length and max new tokens. Fast: 330 max new tokens, 600 cache length.
                        """
            )
            with gr.Row():
                max_new_tokens = gr.Slider(
                    label="Max new tokens",
                    minimum=100,
                    maximum=1000,
                    value=1000,
                    step=10,
                )
                max_cache_len = gr.Slider(
                    label="Cache length",
                    minimum=200,
                    maximum=1500,
                    value=1500,
                    step=10,
                )
            use_compilation = gr.Checkbox(
                label="Use compilation", value=None, visible=True
            )

    inputs = {
        exaggeration: "exaggeration",
        cfg_weight: "cfg_weight",
        temperature: "temperature",
        # audio_prompt_path: "audio_prompt_path",
        # seed: "seed",
        # model
        device: "device",
        dtype: "dtype",
        model_name: "model_name",
        # hyperparameters
        chunked: "chunked",
        cpu_offload: "cpu_offload",
        cache_voice: "cache_voice",
        # chunks
        desired_length: "desired_length",
        max_length: "max_length",
        halve_first_chunk: "halve_first_chunk",
        # compile
        use_compilation: "use_compilation",
        # optimization
        max_new_tokens: "max_new_tokens",
        max_cache_len: "max_cache_len",
    }

    for component, name in inputs.items():
        component.change(
            fn=update_generation_params("chatterbox")(name), inputs=component
        )
        # .then(
        #     fn=lambda: print(generation_params_by_model["chatterbox"])
        # )

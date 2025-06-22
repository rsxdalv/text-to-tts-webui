# [TTS WebUI](https://github.com/rsxdalv/tts-webui) Extension for [Oobabooga Text Generation WebUI](https://github.com/oobabooga/text-generation-webui)

Enhance your text generation experience with the Kokoro TTS extension, seamlessly integrating with the Oobabooga Text Generation WebUI.

## License

- **Project License:** This extension is released under the [MIT License](LICENSE) and is built upon the [Original Kokoro 82M Inference Code](https://huggingface.co/hexgrad/Kokoro-82M/tree/c97b7bbc3e60f447383c79b2f94fee861ff156ac).

- **Model Weights:** The model weights are **not** covered by the MIT License. They are licensed under the [Apache 2.0 License](https://huggingface.co/hexgrad/Kokoro-82M) and will be directly downloaded from Hugging Face.

## Installation

Install [TTS WebUI](https://github.com/rsxdalv/tts-webui) and activate the OpenAI compatible TTS API under *Tools > OpenAI API*.

Once TTS WebUI's OpenAI API is running, you can install this extension by following the instructions below:

1. Clone this repository into the `extensions` directory of your Oobabooga Text Generation WebUI installation.
2. Install the required dependencies by running `pip install -r requirements.txt` in the extension's directory.
3. Restart the Oobabooga Text Generation WebUI.

## Acknowledgements

This extension is built upon the [KokoroTtsTexGernerationWebui](https://github.com/h43lb1t0/KokoroTtsTexGernerationWebui) repository by [Tom Haelbich](https://github.com/h43lb1t0). License of his work is in the [LICENSE.derived](LICENSE.derived) file.

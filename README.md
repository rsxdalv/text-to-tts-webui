### Kokoro based TTS Extension for obabooga text gereration webui

#### License
This project is licensed under the MIT License and is based on the [Original Kokoro 82M Interferance Code](https://huggingface.co/hexgrad/Kokoro-82M).

The Model weights are NOT under the MIT License and are under the [Apache 2.0 License](https://huggingface.co/hexgrad/Kokoro-82M).

#### Installation
This project currently only supports Windows. 
You need to install [espeak](https://github.com/espeak-ng/espeak-ng/releases) and [ffmpeg](https://ffmpeg.org/download.html).

You need to install [Git LFS](https://git-lfs.github.com/) to clone this repo and download the model weights.

You can install the required python packages by running:
```cmd
.\cmd_windows.bat
pip install -r extensions\Kokoro-tts-text-gerneration-webui\requirements.txt
```

#### Features

Kokoro is limited to 510 tokens per input. This extension allows you to generate longer texts by splitting the input into multiple parts and concatenating the outputs.
This is just a workaround and not a perfect solution. If a word is built with multiple tokens, it can happen that the tokensplit is in the middle of the word. This can lead to a bad pronunciation.

#### Roadmap
- [x] Implement the extension
- [ ] Voice selection


#### Contributing
If you want to contribute to this project, feel free to create a pull request.
The code is not perfect and can be improved in many ways.

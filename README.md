### Kokoro based TTS Extension for [obabooga text gereration webui](https://github.com/oobabooga/text-generation-webui)

#### License
This project is licensed under the MIT License and is based on the [Original Kokoro 82M Interferance Code](https://huggingface.co/hexgrad/Kokoro-82M/tree/c97b7bbc3e60f447383c79b2f94fee861ff156ac).

The Model weights are NOT under the MIT License and are under the [Apache 2.0 License](https://huggingface.co/hexgrad/Kokoro-82M). The model wights will be directly downloaded from the Huggingface.

#### Installation
You need to install [espeak](https://github.com/espeak-ng/espeak-ng/releases) and [ffmpeg](https://ffmpeg.org/download.html).


You can install the required python packages by running:
```cmd
.\cmd_windows.bat
pip install -r extensions\KokoroTtsTextGernerationWebui\requirements.txt
```

```bash
./cmd_linux.sh
pip install -r extensions/KokoroTtsTextGernerationWebui/requirements.txt
```


#### Features

Kokoro is limited to 510 tokens per input. This extension allows you to generate longer texts by splitting the input into multiple parts and concatenating the outputs.

The following methods for this are available:

- *Split by Sentance* - The Input is split into Chunks of Sentances that are less than 510 tokens.
- *Split by Word* - The Input is split into Chunks of Words that are less than 510 tokens.

The first method is recommended as it will keep the context of the text and results in better output quality.

#### Multiple GPU
If you have multiple GPUs, the first one will be used by default. You can change that in `src/generate.py` by setting the `device` variable to the desired GPU.

#### Roadmap
- [x] Implement the extension
- [x] Support all OS
- [x] Voice selection


#### Contributing
If you want to contribute to this project, feel free to create a pull request.
The code is not perfect and can be improved in many ways.

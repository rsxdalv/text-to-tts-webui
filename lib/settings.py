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
    "hexgrad/Kokoro-82M": {},
    "chatterbox": {
        "exaggeration": 0.5,
        "cfg_weight": 0.5,
        "temperature": 0.8,
        "dtype": "float32",
    },
}


def update_setting(setting):
    def inner(value):
        global settings
        settings[setting] = value

    return inner


def update_voice(model):
    def inner(voice):
        global voice_by_model
        voice_by_model[model] = voice

    return inner


def update_generation_params(model):
    def inner(param):
        def inner2(value):
            global generation_params_by_model
            generation_params_by_model[model][param] = value

        return inner2

    return inner

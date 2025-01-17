import uuid
from .models import build_model
import torch
import os
from transformers import AutoTokenizer
import numpy as np
from pydub import AudioSegment
import pathlib
from huggingface_hub import snapshot_download
from modules import shared
from .voices import VOICES



snapshot_download(repo_id="hexgrad/Kokoro-82M", cache_dir =pathlib.Path(__file__).parent, allow_patterns=["*.pth", "*.pt"])

if os.name == 'nt':
    os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
    os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG\espeak-ng.exe"

from .kokoro import generate, tokenize, phonemize

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_path = pathlib.Path(__file__).parent / 'models--hexgrad--Kokoro-82M' / 'snapshots' / 'e78b910980f63ec856f07ba02a24752a5ab7af5b' / 'kokoro-v0_19.pth'
MODEL = build_model(model_path, device)

voice_name, voicepack = None, None

def load_voice(voice=None):
    global voice_name, voicepack
    voice_name = voice or VOICES[0]
    voise_path = pathlib.Path(__file__).parent / 'models--hexgrad--Kokoro-82M' / 'snapshots' / 'e78b910980f63ec856f07ba02a24752a5ab7af5b' / 'voices' / f'{voice_name}.pt'
    voicepack = torch.load(voise_path, weights_only=True).to(device)
    print(f'Loaded voice: {voice_name}')

load_voice()



def run(text, preview=False):
    msg_id = str(uuid.uuid4())
    ps = phonemize(text, lang=voice_name[0])
    tokenized_text = tokenize(ps)
    out = split_text(tokenized_text)
    segments = generate_audio_chunks(out)
    full_adio = concatenate_audio_segments(segments)

    audio_path = pathlib.Path(__file__).parent / '..' / 'audio' / f'{"preview" if preview else msg_id}.wav'
    full_adio.export(audio_path, format="wav")

    return msg_id

def split_text(tokenized_text):
    
    chunk_size = 510

    if len(tokenized_text) > chunk_size:
        print(f'Text is too long ({len(tokenized_text)} tokens), splitting into chunks of {chunk_size} tokens')
        chunks = [
            tokenized_text[i:i + chunk_size]
            for i in range(0, len(tokenized_text), chunk_size)
        ]
    else:
        chunks = [tokenized_text]

    out = {'out': [], 'ps': []}
    for i, chunk in enumerate(chunks):
        out_chunk, ps = generate(MODEL, chunk, voicepack, lang=voice_name[0])
        out['out'].append(out_chunk)
        out['ps'].append(ps)

    return out


def generate_audio_chunks(out):
    segments = []

    for i, chunk in enumerate(out['out']):
        # Normalize to 16-bit PCM
        normalized_audio = np.int16(chunk / np.max(np.abs(chunk)) * 32767)

        # Create an AudioSegment
        segments.append(AudioSegment(
            data=normalized_audio.tobytes(),
            sample_width=normalized_audio.dtype.itemsize,  # 2 bytes for int16
            frame_rate=24000,
            channels=1
        ))

    return segments

def concatenate_audio_segments(segments):

    # Concatenate all segments
    audio_segment = segments[0]
    for segment in segments[1:]:
        audio_segment += segment

    return audio_segment

if __name__ == '__main__':
    run("Hello, this is an example of a text for Kokoro")
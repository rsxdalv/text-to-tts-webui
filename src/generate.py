import uuid
from .models import build_model
import torch
import os
from transformers import AutoTokenizer
import numpy as np
from pydub import AudioSegment
import pathlib

os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG\espeak-ng.exe"

from .kokoro import generate, tokenize, phonemize

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_path = pathlib.Path(__file__).parent / 'kokoro-v0_19.pth'
MODEL = build_model(model_path, device)
VOICE_NAME = [
    'af', # Default voice is a 50-50 mix of Bella & Sarah
    'af_bella', 'af_sarah', 'am_adam', 'am_michael',
    'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
    'af_nicole', 'af_sky',
][5]
voise_path = pathlib.Path(__file__).parent / 'voices' / f'{VOICE_NAME}.pt'
VOICEPACK = torch.load(voise_path, weights_only=True).to(device)
print(f'Loaded voice: {VOICE_NAME}')

def run(text):
    msg_id = str(uuid.uuid4())
    ps = phonemize(text, lang=VOICE_NAME[0])
    tokenized_text = tokenize(ps)
    out = split_text(tokenized_text)
    segments = generate_audio_chunks(out)
    full_adio = concatenate_audio_segments(segments)

    audio_path = pathlib.Path(__file__).parent / '..' / 'audio' / f'{msg_id}.wav'

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
        out_chunk, ps = generate(MODEL, chunk, VOICEPACK, lang=VOICE_NAME[0])
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
import uuid
from .models import build_model
import torch
import os
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
    out = split_text(text)
    segments = generate_audio_chunks(out)
    full_adio = concatenate_audio_segments(segments)

    audio_path = pathlib.Path(__file__).parent / '..' / 'audio' / f'{"preview" if preview else msg_id}.wav'
    full_adio.export(audio_path, format="wav")

    return msg_id

def split_text(text):
    
    max_token = 510
    words = text.split()
    current_words = []
    chunks = []
    current_chunk_len = 0

    tokenized_text = tokenize(phonemize(text, lang=voice_name[0]))
    if len(tokenized_text) > max_token:
        for word in words:
            tokenized_word = tokenize(phonemize(word, lang=voice_name[0]))
            additional_tokens = len(tokenized_word) + (1 if current_words else 0)
            # Check if adding this word exceeds the token limit
            if current_chunk_len + additional_tokens > max_token and current_words:
                current_text = ' '.join(current_words)
                tokenized_chunk = tokenize(phonemize(current_text, lang=voice_name[0]))
                print(f'Chunk length: {len(tokenized_chunk)}')
                chunks.append(tokenized_chunk)
                current_words = []
                current_chunk_len = 0

            else:
                current_words.append(word)
                current_chunk_len += additional_tokens

        # Add remaining words as the final chunk if any
        if current_words:
            current_text = ' '.join(current_words)
            tokenized_chunk = tokenize(phonemize(current_text, lang=voice_name[0]))
            print(f'Chunk length: {len(tokenized_chunk)}')
            chunks.append(tokenized_chunk)

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
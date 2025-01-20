import gc
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
from nltk.tokenize import sent_tokenize
import nltk


snapshot_download(repo_id="hexgrad/Kokoro-82M", cache_dir =pathlib.Path(__file__).parent, allow_patterns=["*.pth", "*.pt"])
nltk.download('punkt')
nltk.download('punkt_tab')

if os.name == 'nt':
    os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
    os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG\espeak-ng.exe"

from .kokoro import generate, tokenize, phonemize

device = 'cuda' if torch.cuda.is_available() else 'cpu'


snapshot_path = pathlib.Path(__file__).parent / 'models--hexgrad--Kokoro-82M' / 'snapshots'
snapshot_path = snapshot_path / os.listdir(snapshot_path)[0]

model_path = snapshot_path / 'kokoro-v0_19.pth'
MODEL = None

voice_name, voicepack = None, None

def load_voice(voice=None):
    global voice_name, voicepack
    voice_name = voice or VOICES[0]
    voise_path = snapshot_path / 'voices' / f'{voice_name}.pt'
    voicepack = torch.load(voise_path, weights_only=True).to(device)
    print(f'Loaded voice: {voice_name}')


load_voice()


def run(text, preview=False):
    global MODEL, voicepack
    MODEL = build_model(model_path, device)
    msg_id = str(uuid.uuid4())
    out = split_text(text)
    segments = generate_audio_chunks(out)
    full_adio = concatenate_audio_segments(segments)
    audio_path = pathlib.Path(__file__).parent / '..' / 'audio' / f'{"preview" if preview else msg_id}.wav'
    full_adio.export(audio_path, format="wav")

    del MODEL
    gc.collect()

    return msg_id

sentance_based = True

def set_plitting_type(method="Split by Sentance"):
    global sentance_based
    sentance_based = True if method == "Split by Sentance" else False
    print(f'Splitting method: {"Sentance" if sentance_based else "Word"}')

set_plitting_type()

def split_text(text):

    global MODEL
    
    max_token = 510
    text_parts = sent_tokenize(text) if sentance_based else text.split()
    current_text_parts = []
    chunks = []
    current_chunk_len = 0



    for text_part in text_parts:
        tokenized_textpart = tokenize(phonemize(text_part, lang=voice_name[0]))
        additional_tokens = len(tokenized_textpart) + 1

        if current_chunk_len + additional_tokens > max_token and current_text_parts:
            # Create the chunk from what's accumulated so far
            current_text = ' '.join(current_text_parts)
            tokenized_chunk = tokenize(phonemize(current_text, lang=voice_name[0]))
            chunks.append(tokenized_chunk)

            # Reset trackers
            current_text_parts = []
            current_chunk_len = 0

            
        current_text_parts.append(text_part)
        current_chunk_len += additional_tokens


    # Add remaining words as the final chunk if any
    if current_text_parts:
        current_text = ' '.join(current_text_parts)
        tokenized_chunk = tokenize(phonemize(current_text, lang=voice_name[0]))
        chunks.append(tokenized_chunk)


    del text_parts

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
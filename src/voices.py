import os
import pathlib

snapshot_path = pathlib.Path(__file__).parent / 'models--hexgrad--Kokoro-82M' / 'snapshots'
snapshot_path = snapshot_path / os.listdir(snapshot_path)[0]
voices = os.listdir(snapshot_path / 'voices')
VOICES = [voice.replace('.pt', '') for voice in voices]

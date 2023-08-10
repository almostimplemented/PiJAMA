import piano_transcription_inference as hr

from pathlib import Path
from tqdm import tqdm

MIDI_ROOT = "data/midi_kong"
AUDIO_ROOT = "data/resampled"

transcriber = hr.PianoTranscription(device='cuda')

audio_root = Path(AUDIO_ROOT)
mp3_files = list(audio_root.glob("*/**/*.mp3"))

for mp3_file in tqdm(mp3_files):
    midi_out = Path(MIDI_ROOT, *mp3_file.with_suffix(".midi").parts[2:])
    if midi_out.exists():
        print("Skipping existing MIDI:", midi_out)
        continue
    midi_out.parent.mkdir(parents=True, exist_ok=True)
    (audio, _) = hr.load_audio(mp3_file, sr=None)
    _ = transcriber.transcribe(audio, midi_out)

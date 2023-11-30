import urllib.request
import zipfile
from pathlib import Path

# create data directory if it doesn't exist
PROJECT_ROOT = Path(__file__).parent.parent
data_dir = PROJECT_ROOT / 'data'
data_dir.mkdir(parents=True, exist_ok=True)

# download and unzip midi_hawthorne.zip
url1 = "https://zenodo.org/records/8354955/files/midi_hawthorne.zip?download=1"
print("Downloading Onsets and Frames MIDI transcriptions ... ")
urllib.request.urlretrieve(url1, data_dir / "midi_hawthorne.zip")
print("Extracting Onsets and Frames MIDI transcriptions ... to midi/")
with zipfile.ZipFile(data_dir / "midi_hawthorne.zip", "r") as zip_ref:
    zip_ref.extractall(data_dir)

# download and unzip midi_kong.zip
url2 = "https://zenodo.org/records/8354955/files/midi_kong.zip?download=1"
print("Downloading Onsets and Frames MIDI transcriptions ... ")
urllib.request.urlretrieve(url2, data_dir / "midi_kong.zip")
print("Extracting Onsets and Frames MIDI transcriptions ... to midi_kong/")
with zipfile.ZipFile(data_dir / "midi_kong.zip", "r") as zip_ref:
    zip_ref.extractall(data_dir)

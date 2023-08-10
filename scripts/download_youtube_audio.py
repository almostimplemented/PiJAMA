import pandas as pd
import youtube_dl

from pathlib import Path

df = pd.read_csv("pijama.csv")

ydl_opts = {
    'audioformat' : "mp3",      # convert to mp3
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

n_errors = 0
n_success = 0
for record in df.itertuples():
    print(f"Attempting to download {record.title} ({record.artist}, {record.album})")
    url = record.youtube_url
    output_path = Path(record.mp3_filepath)
    if output_path.exists():
        print("Skipping existing MP3: ", output_path)
        continue
    ydl_opts["outtmpl"] = f"{output_path.with_suffix('')}.%(ext)s"
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            n_success += 1
        except Exception as e:
            n_errors += 1
            print(f"Error downloading YouTube URL: {url}")
            print(e)

print("Total number of errors:", n_errors)
print("Total number of successful downloads:", n_success)

import csv
import functools
from mutagen.mp3 import MP3
import os
from pathlib import Path
import random

CSV_FILENAME = "pijama.csv"


class Track:
    """
    Represents a piano performance
    Stores the title, artist, album, recording condition, and relative path

    Computes the duration on-demand
    """

    def __init__(
        self,
        title,
        artist,
        album,
        recording_condition,
        midi_filepath,
        mp3_filepath,
        youtube_url,
        duration_sec,
        performance_start_sec=0,
        performance_end_sec=None,
        split=None,
    ):
        self.title = title
        self.artist = artist
        self.album = album
        self.recording_condition = recording_condition
        self.midi_filepath = midi_filepath
        self.mp3_filepath = mp3_filepath
        self.youtube_url = youtube_url
        self.duration_sec = duration_sec
        self.performance_start_sec = performance_start_sec
        self.performance_end_sec = performance_end_sec if performance_end_sec else duration_sec
        self.split = split

    @property
    def performance_duration_sec(self):
        if self.performance_end_sec is None or self.performance_start_sec is None:
            return self.duration_sec
        return self.performance_end_sec - self.performance_start_sec

    def __repr__(self):
        return f"Track({self.title} | {self.artist} | {self.album})"


def read_tracks_from_csv(csv_filepath=CSV_FILENAME):
    tracks = []
    with open(csv_filepath) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            tracks.append(
                Track(
                    row["title"],
                    row["artist"],
                    row["album"],
                    row["recording_condition"],
                    row["midi_filepath"],
                    row["mp3_filepath"],
                    row["youtube_url"],
                    float(row["duration_sec"]),
                    float(row["performance_start_sec"]),
                    float(row["performance_end_sec"]),
                    row["split"],
                )
            )

    return tracks


def read_tracks_from_file_hierarchy(recording_condition):
    tracks = []
    audio_root = Path("data", "audio", recording_condition)
    midi_root = Path("data", "midi", recording_condition)
    artists = os.listdir(audio_root)
    for artist in artists:
        artist_path = Path(audio_root, artist)
        if not artist_path.is_dir():
            continue
        for album in os.listdir(artist_path):
            album_path = Path(artist_path, album)
            if not album_path.is_dir():
                continue
            for t in os.listdir(album_path):
                mp3_path = Path(album_path, t)
                mp3 = MP3(mp3_path)
                if "COMM::XXX" not in mp3:
                    print("Warning: no YouTube link found for: ", mp3_path)
                    continue
                youtube_url = mp3["COMM::XXX"].text[0]
                duration = mp3.info.length
                title = mp3_path.stem
                _midi_path = Path(midi_root, artist, album, t)
                midi_path = _midi_path.with_suffix(".midi")
                if not midi_path.is_file():
                    print("Error: no MIDI file found at:", midi_path)
                    midi_path = None
                track = Track(
                    title,
                    artist,
                    album,
                    recording_condition,
                    midi_path,
                    mp3_path,
                    youtube_url,
                    duration,
                )
                tracks.append(track)
    return tracks


def write_metadata(tracks, csv_filename=CSV_FILENAME):
    with open(csv_filename, "w") as f:
        writer = csv.writer(f)
        headers = (
            "artist",
            "album",
            "title",
            "recording_condition",
            "midi_filepath",
            "mp3_filepath",
            "youtube_url",
            "duration_sec",
            "performance_start_sec",
            "performance_end_sec",
            "split",
        )
        writer.writerow(headers)
        for track in tracks:
            writer.writerow(
                (
                    track.artist,
                    track.album,
                    track.title,
                    track.recording_condition,
                    track.midi_filepath,
                    track.mp3_filepath,
                    track.youtube_url,
                    track.duration_sec,
                    track.performance_start_sec,
                    track.performance_end_sec,
                    track.split,
                )
            )


def assign_random_splits(tracks, seed=42, split_ratios=(0.8, 0.1, 0.1)):
    if not isinstance(split_ratios, tuple):
        raise TypeError("Expected tuple, got {type(split_ratios)} (split_ratios)")
    if len(split_ratios) != 3 or sum(split_ratios) != 1:
        raise TypeError("split_ratios must be a three element tuple that sums to 1")

    # Compute split duration limits
    total_duration = sum([t.duration_sec for t in tracks])
    train_duration_limit = split_ratios[0] * total_duration
    test_duration_limit = split_ratios[1] * total_duration
    train_duration = 0
    test_duration = 0

    random.Random(seed).shuffle(tracks)
    shuffled_tracks_it = iter(tracks)

    for track in shuffled_tracks_it:
        if train_duration > train_duration_limit:
            test_duration += track.duration_sec
            track.split = "test"
            break
        train_duration += track.duration_sec
        track.split = "train"
    for track in shuffled_tracks_it:
        if test_duration > test_duration_limit:
            track.split = "val"
            break
        test_duration += track.duration_sec
        track.split = "test"
    for track in shuffled_tracks_it:
        track.split = "val"

    return tracks


if __name__ == "__main__":
    studio_tracks = read_tracks_from_file_hierarchy("studio")
    live_tracks = read_tracks_from_file_hierarchy("live")
    assign_random_splits(live_tracks)
    assign_random_splits(studio_tracks)
    tracks = studio_tracks + live_tracks
    write_metadata(tracks)

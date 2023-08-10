import itertools
import metadata
import note_seq
import os
import shutil
import tempfile

from magenta.scripts import convert_dir_to_note_sequences
from tqdm import tqdm


def generate_note_sequences():
    all_tracks = metadata.read_tracks_from_csv()
    split_it = itertools.groupby(all_tracks, lambda t: t.split)

    for split, tracks in split_it:
        print("Generating", split, "split ...")
        with tempfile.TemporaryDirectory() as split_dir:
            for track in tqdm(tracks):
                shutil.copy(track.midi_filepath, split_dir)
            output_filepath = split + "_notesequences.tfrecord"
            convert_dir_to_note_sequences.convert_directory(
                split_dir, output_filepath, recursive=True
            )


if __name__ == "__main__":
    generate_note_sequences()

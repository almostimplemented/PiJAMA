import metadata
import numpy as np
import pickle
from pathlib import Path


def max_class_vector(cav):
    # speech = 0, applause = 1, music = 2
    stacked = np.stack([cav["speech"], cav["applause"], cav["music"]])
    return np.argmax(stacked, axis=0)


def longest_clean_section(cav):
    max_run = 0
    cur_run = 0
    cur_run_start_idx = -1
    max_run_start_idx = -1

    for i, x in enumerate(max_class_vector(cav)):
        if (x == 2 and cav["applause"][i] < 0.4 and cav["speech"][i] < 0.5) or (
            x != 2 and cav["applause"][i] < 0.1 and cav["speech"][i] < 0.1
        ):
            cur_run += 1
            if cur_run_start_idx == -1:
                cur_run_start_idx = i
        else:
            if cur_run > max_run:
                max_run = cur_run
                max_run_start_idx = cur_run_start_idx
            cur_run = 0
            cur_run_start_idx = -1

    if cur_run > max_run:
        max_run = cur_run
        max_run_start_idx = cur_run_start_idx

    return max_run_start_idx, max_run


# convert the track's audio path to a key in the pickled class activations scores dict
def audio_path_to_dict_key(p):
    root = Path("/import/c4dm-datasets/PiJAMA/data/resampled/")
    relative_path = Path(*Path(p).parts[2:])
    return Path(root, relative_path)



if __name__ == "__main__":
    tracks = metadata.read_tracks_from_csv()

    with open("fp_to_class_scores.pkl", "rb") as f:
        d = pickle.load(f)

    total_performance_duration = 0
    total_duration = 0

    for t in tracks:
        k = audio_path_to_dict_key(t.mp3_filepath)
        if k not in d:
            print("No inference found for track:", t, t.mp3_filepath)
            continue

        class_activation_vector = d[k]
        start, length = longest_clean_section(class_activation_vector)
        t.performance_start_sec = start
        t.performance_end_sec = start + length
        total_duration += t.duration_sec
        total_performance_duration += length

        if t.duration_sec > 2 * t.performance_duration_sec:
            print(
                "Excessive gap: ",
                t,
                "performance duration:",
                t.performance_duration_sec,
                "total duration:",
                t.duration_sec,
                "start:",
                start,
                "end:",
                start + length,
            )

    print("Total duration (hours):", total_duration / 3600)
    print("Total performance duration (hours):", total_performance_duration / 3600)
    metadata.write_metadata(tracks)

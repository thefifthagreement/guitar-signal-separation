from pathlib import Path
import numpy as np
from scipy.io import wavfile
import librosa
from tqdm import tqdm

wd_path = Path.cwd()

# umx data folder
umx_data_path = wd_path.joinpath("data")

max_duration =  180

def split_duration(split):
    parent = ""
    durations = {}
    durations_values = []
    for f in umx_data_path.joinpath(split).glob("**/*"):
        if f.is_file():
            if parent != f.parent.name:
                parent = f.parent.name
                duration = librosa.get_duration(filename=f)
                durations[parent] = duration

    durations_values = [d for d in durations.values()]
    return [max(durations_values), min(durations_values), np.mean(durations_values)]

def limit_duration():
    for f in tqdm(umx_data_path.joinpath("stems").glob("**/*.wav")):
        rate, wav = wavfile.read(f)
        if wav.shape[0] // rate > max_duration:
            wav = wav[0:max_duration*rate]
            wavfile.write(f, rate, wav)

if __name__ == "__main__":
    print("train split min/max/mean durations: {:.2f}/{:.2f}/{:.2f},\ntest split min/max durations: {:.2f}/{:.2f}/{:.2f}" \
        .format(*split_duration("train"), *split_duration("valid")))

    print("stems min/max/mean durations: {:.2f}/{:.2f}/{:.2f}".format(*split_duration("stems")))


"""

Preprocessing steps for the VariableSourcesTrackFolderDataset type (trackfolder_var)

Given the target, filter the songs containing STEMS of this target, the target must be unique
Split the songs in train, valid
In the data folder, create a train and valid folder, then create 1 folder by song in the correct split folder

"""
from pathlib import Path
from tqdm import tqdm
from scipy.io import wavfile

# dossier de travail
umx_path = Path("D:\github\jedha-final-project\open-unmix")

# dossier de données
data_path = Path("D:\Mickaël\Documents\MIR\Medley\MedleyDB_V1\V1")

# train, test split the stems
train_path = umx_path.joinpath("data", "train")
test_path = umx_path.joinpath("data", "valid")

# sélection de pistes pour le test du modèle
train_tracks = {
    "CroqueMadame_Oil": "02", 
    "MusicDelta_Shadows": "03"
}
test_tracks = {"CroqueMadame_Pilot": "02"}

# chemin vers les STEMS
train_track_path = [data_path.joinpath(c, c+"_STEMS") for c in train_tracks]
test_track_path = [data_path.joinpath(c, c+"_STEMS") for c in test_tracks]

# chemins des STEMS
train_fns = [t.joinpath(c + "_STEM_" + train_tracks[c] + ".wav") for c, t in zip(train_tracks, train_track_path)]
test_fns = [t.joinpath(c + "_STEM_" + test_tracks[c] + ".wav") for c, t in zip(test_tracks, test_track_path)]

for split, fns in zip([train_path, test_path], [train_fns, test_fns]):
    # longueur de chaque morceau de piste envoyée au modèle = 6 secondes
    interval = 44100 * 6
    for fn in tqdm(fns):
        rate, wav = wavfile.read(fn)
        # nombre de samples de 6 secondes possible dans le STEM
        stop = (wav.shape[0]//interval) * interval

        # création des samples de 6 secondes
        sample_name = fn.name.split(".")[0]
        for i in range(0, stop - interval, interval):
            sample = wav[i:i+interval]
            i = int(i/interval)
            save_fn = split.joinpath(f"{sample_name}_{i}.wav")
            if save_fn.exists():
                continue
            wavfile.write(
                filename=save_fn, 
                rate=rate, 
                data=sample
            )

            





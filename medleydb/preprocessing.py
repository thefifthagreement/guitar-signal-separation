# -*- coding: utf-8 -*-
"""
MedleyDB preprocessing steps for the VariableSourcesTrackFolderDataset type (trackfolder_var)

Given the target, filter the songs containing STEMS of this target, the target must be unique
Split the songs in train, valid
In the data folder, create a train and valid folder, then create 1 folder by song in the correct split folder
"""
from os import environ
from shutil import copytree
from pathlib import Path
from tqdm import tqdm
import numpy as np
from random import sample
import pandas as pd
from scipy.io import wavfile
from librosa import load
import soundfile as sf
from sklearn.model_selection import train_test_split
from medleydb.utils import get_instrument_stems, get_instrument_tracks, get_instruments_dict, get_instruments_list, get_instrument_ratio
from cambridge.utils import processing_tracks as cambridge_processing

wd_path = Path.cwd()

# metadata table
data_path = wd_path.joinpath("data")

# data folder for the open-unmix model
umx_data_path = Path("/media/mvitry/Windows/umx/data")

# folder of the dataset, mixes and stems
medleydb_path = Path(environ['MEDLEYDB_PATH'])

# medleyDB repo data path
metadata_path = Path(environ['METADATA_PATH']) 

# path to activation files in the medleyDB local repository
activation_path = metadata_path.joinpath("medleydb", "data", "Annotations", "Activation_Confidence", "all")

# limiting the duration of the STEMS (seconds)
max_duration = 180

def pre_processing(metadata_df, target_instrument_name, copy_folders=True, stereo=True):

    STEMS = metadata_df["stems"]

    # target instrument presence ratio in the target instrument tracks
    target_track_activations, _ = get_instrument_ratio(metadata_df["stems"], activation_path, target_instrument_name)

    # listing the track with a ratio more than 60%
    instrument_tracks = [track for track, ratio in target_track_activations.items() if ratio > 0.6]

    print(f"Pre-processing of the audio files, the target instrument is {target_instrument_name}.")
    print(f"{len(instrument_tracks)} tracks containing the target.")

    # the folder of the original STEMS
    instrument_folders = sorted([medleydb_path.joinpath(t, f"{t}_STEMS") for t in instrument_tracks])

    # the folder where to copy the STEMS for the preprocessing
    umx_stems_folders = [umx_data_path.joinpath("stems", f.name) for f in instrument_folders]
    
    # if the copy is needed
    if copy_folders:
        # copy the target STEMS in open-unmix source folder before renaming or fusion
        print("Copying the stems folders...")
        for i in tqdm(range(len(instrument_folders))):
            copytree(instrument_folders[i], umx_stems_folders[i])

        # renaming the STEMS except the target using the instrument dict
        instruments_dict = get_instruments_dict(get_instruments_list(STEMS))

        # for each track we rename the STEMS using their instrument name
        # if the target instrument is in more than 1 stem, we sum the corresponding wav files
        print("Renaming the files using the instrument name")
        for track_path in tqdm(umx_stems_folders):
            # the stems of the current track
            track_stems = metadata_df.query(f"stem_dir == '{track_path.name}'")["stems"].iloc[0]
            track_stems = eval(track_stems)

            # instrument counter
            stem_instruments = {}

            for stem in track_stems.values():
                instrument = stem["instrument"]

                # instrument counter to avoid same file name: instrument_#.wav
                if instrument in stem_instruments:
                    stem_instruments[instrument] += 1
                else:
                    stem_instruments[instrument] = 1

                # it's not the target instrument we remame the file
                if instrument != target_instrument_name:
                    stem_file = track_path.joinpath(stem["filename"])
                    stem_file.rename(track_path.joinpath(f"{instruments_dict[instrument]}_{stem_instruments[instrument]}.wav"))

            # if there is more than 1 stem for the target instrument
            if stem_instruments[target_instrument_name] > 1:
                # target files fusion
                rate = 44100 # default sampling rate
                files = []
                target_file = np.empty
                for f in track_path.glob(f"{track_path.name.split('_')[0]}*"): # the files names are like trackname_*
                    if f.is_file():
                        wav, _ = load(f, sr=rate)
                        files.append(wav)
                    # deleting the partial target file 
                    f.unlink()

                # summing the wav files
                target_file = sum(files)

                # writing the fusionned target wav file
                sf.write(track_path.joinpath(f"{instruments_dict[target_instrument_name]}.wav"), data=target_file, samplerate=rate)
            else:
                # target instrument file rename
                for f in track_path.glob(f"{track_path.name.split('_')[0]}*"): # the file name is like trackname_*
                    if f.is_file():
                        f.rename(track_path.joinpath(f"{instruments_dict[target_instrument_name]}.wav"))

    if not stereo:
        # making mono files
        print("making mono audio...")
        for f in tqdm(umx_data_path.joinpath("stems").glob("**/*.wav")):
            wav, sr = load(f, sr=None)
            sf.write(f, wav, sr)
    
    return umx_stems_folders

def copy_split(split, folders):
    """
    Create the split folders and copy the files
    """
    umx_data_path.joinpath(split).mkdir()
    print(f"Copying {split} split files...")
    for folder in tqdm(folders):
        umx_data_path.joinpath(split, folder.name).mkdir()
        copytree(folder, umx_data_path.joinpath(split, folder.name), dirs_exist_ok=True)

def train_valid_split(umx_stems_folders, nb_sample=0):
    """
    Split the tracks into train and valid folders
    sample: the size of the sample of folders for testing purpose
    """

    if nb_sample > 0:
        umx_stems_folders = sample(umx_stems_folders, nb_sample)

    print("Spliting in train valid folders...")
    train, valid = train_test_split(umx_stems_folders, test_size=0.2, random_state=42)
    copy_split("train", train)
    copy_split("valid", valid)


if __name__ == "__main__":
    # MedleyDB metadata
    metadata_df = pd.read_csv(data_path.joinpath("metadata.csv"))

    # target instrument
    instrument_name = "acoustic guitar"
    target_instrument_name = get_instruments_dict(get_instruments_list(metadata_df["stems"]))[instrument_name]

    # Cambridge Music Technology add files
    cambridge_audio_path = Path("/media/mvitry/7632099B3209620B/Mickaël/Documents/MIR/Cambridge Music Technology/acoustic guitar")
    cambridge_processing(cambridge_audio_path, target_instrument_name, copy_folders=False)

    # preprocessing the STEMS, returning the folders with the correct files
    pre_processing(metadata_df, instrument_name, copy_folders=False, stereo=True)

    umx_stems_folders = [f for f in umx_data_path.joinpath("stems").iterdir()]

    # divide the dataset and create the folder architecture for the training
    train_valid_split(umx_stems_folders)
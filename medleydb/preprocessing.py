# -*- coding: utf-8 -*-
"""
MedleyDB preprocessing
"""
from os import environ
from shutil import copytree
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from medleydb.utils import get_instrument_stems, get_instrument_tracks, get_instruments_dict, get_instruments_list

wd_path = Path.cwd()

# metadata table
metadata_path = wd_path.joinpath("data")

# data folder for the open-unmix model
umix_data_path = wd_path.parent.joinpath("open-unmix", "data")

# folder of the dataset, mixes and stems
medleydb_path = Path(environ['MEDLEYDB_PATH'])

if __name__ == "__main__":

    # MedleyDB metadata
    metadata_df = pd.read_csv(metadata_path.joinpath("metadata.csv"))
    STEMS = metadata_df["stems"]

    # target instrument
    instrument_name = "clean electric guitar"

    # list of target instrument folders
    instrument_stems = get_instrument_stems(STEMS, instrument_name)
    instrument_tracks = get_instrument_tracks(instrument_stems, instrument_name)

    instrument_folders = sorted([medleydb_path.joinpath(t, f"{t}_STEMS") for t in instrument_tracks])
    umix_stems_folders = [umix_data_path.joinpath("stems", f.name) for f in instrument_folders]

    # copy the target STEMS in open-unmix source folder before renaming and split
    #for i in range(len(instrument_folders)):
    #    copytree(instrument_folders[i], umix_stems_folders[i])

    # renaming the STEMS except the target using the instrument dict
    instruments_dict = get_instruments_dict(get_instruments_list(STEMS))

    for i, track_path in enumerate(umix_stems_folders[:1]):
        track_stems = metadata_df.query(f"stem_dir == '{track_path.name}'")["stems"].iloc[0]
        track_stems = eval(track_stems)

        for stem in track_stems.values():
            print(stem["instrument"], track_path.joinpath(stem["filename"]))


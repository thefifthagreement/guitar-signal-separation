# -*- coding: utf-8 -*-
"""
Utilities to get list from MedleyDB metadata
"""
from os import environ
import numpy as np
import pandas as pd
from pathlib import Path
from librosa import load
import soundfile as sf

def get_instruments_list(stems) -> list:
    """
    Returns a list of unique instruments

    stems: a Pandas series containing the "stems" column of the metadata dataframe
    """
    instruments_list = []
    for stem in stems:
        stem = eval(stem)
        for s in stem.values():
            instruments_list.append(s["instrument"])

    return list(set(instruments_list))

def get_instruments_dict(instruments_list):
    """
    Returns a dict {'instrument 1': 'intrusment_1'}

    instruments_list: a list of unique instruments
    """
    return {i: i.replace(' ', '_').replace("/", '_') for i in instruments_list}

def get_instrument_stems(stems, instrument_name):
    """
    Returns a list of STEMS containing the instrument

    stems: a Pandas series containing the "stems" column of the metadata dataframe
    instrument_name: the name of an instrument
    """
    instrument_stems = []
    for stem in stems:
        stem = eval(stem)
        for s in stem.values():
            if s["instrument"] == instrument_name:
                instrument_stems.append(s["filename"])
    return instrument_stems

def get_instrument_tracks(instrument_stems, instrument_name):
    """
    Returns a list of TRACKS containing the instrument

    instrument_stems: list of STEMS containing the instrument
    instrument_name: the name of an instrument
    """
    return list(sorted(set([s.split("_STEM")[0] for s in instrument_stems])))

def get_track_instruments(track_stems):
    """
    Returns the instrument list of a track

    track_stems: dict of stems of the track   
    """
    track_stems = eval(track_stems)
    track_instruments = []
    for s in track_stems:
        track_instruments.append(track_stems[s]["instrument"])
        
    return list(set(track_instruments))

def get_instrument_ratio(stems, activation_path, instrument_name):
    """
    Returns a dict {track: percentage}
    of the ratio of presence of the instrument in the tracks
    and a list of the missing activation files

    stems: the stems in the metadata dataframe
    activation_path: the activation files path
    instrument_name: the target instrument
    """
    target_stems = get_instrument_stems(stems, instrument_name)
    target_tracks = get_instrument_tracks(target_stems, instrument_name)

    track_activations = {}
    mising_activation_files = []

    for track in target_tracks:
        
        target_activation_path = activation_path.joinpath(track + '_ACTIVATION_CONF.lab')

        stem_id = ['S' + s.split('_')[-1][:2] for s in target_stems if s.split('_STEM')[0] == track]

        if not target_activation_path.exists():
            mising_activation_files.append(track)
            continue
        
        dfx = pd.read_csv(target_activation_path)
        df1 = dfx[stem_id].iloc[:,0] 

        # percentage of the presence of the instrument in the stem
        presence_ratio = (df1 > 0.5).value_counts(True)[1]
        
        track_activations[track] = presence_ratio
    
    return track_activations, mising_activation_files

def get_excerpt(wav_path: Path, offset, duration):
    """
    Create an excerpt from the wav
    """
    wav, sr = load(wav_path, sr=None, offset=offset, duration=duration)
    sf.write(wav_path.parent.joinpath(wav_path.name.split(".")[0] + "_excerpt.wav"), wav, sr)

if __name__ == "__main__":
    wd_path = Path(__file__).parent

    # metadata table path
    data_path = wd_path.parent.joinpath("data")
    metadata_df = pd.read_csv(data_path.joinpath("metadata.csv"))

    instruments_dict = get_instruments_dict(get_instruments_list(metadata_df["stems"]))
    print("instrument list:")
    for k, v in instruments_dict.items():
        print(f"{k}: {v}")

    print()
    target_instrument = "clean electric guitar"
    clean_guitar_stems = get_instrument_stems(metadata_df["stems"], target_instrument)
    clean_guitar_tracks = get_instrument_tracks(clean_guitar_stems, target_instrument)

    print(f"{len(clean_guitar_tracks)} tracks containing {target_instrument} ({len(clean_guitar_tracks)/196:.2%})")

    instruments_0 = get_track_instruments(metadata_df.iloc[0]["stems"])
    print(instruments_0)
# -*- coding: utf-8 -*-
"""
Utilities to get list from MedleyDB metadata
"""

def get_instruments_list(stems):
    """
    stems: a Pandas series containing the "stems" column of the metadata dataframe

    returns a list of unique instruments
    """
    instruments_list = []
    for stem in stems:
        stem = eval(stem)
        for s in stem.values():
            instruments_list.append(s["instrument"])

    return set(instruments_list)

def get_instruments_dict(instruments_list):
    """
    instruments_list: a list of unique instruments

    returns a dict {'instrument 1': 'intrusment_1'}
    """
    return {i: i.replace(' ', '_').replace("/", '_') for i in instruments_list}

def get_instrument_stems(stems, instrument_name):
    """
    stems: a Pandas series containing the "stems" column of the metadata dataframe
    instrument_name: the name of an instrument

    return a list of STEMS containing the instrument
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
    instrument_stems: list of STEMS containing the instrument
    instrument_name: the name of an instrument

    return a list of TRACKS containing the instrument
    """
    return list(set([s.split("_STEM")[0] for s in instrument_stems]))

if __name__ == "__main__":
    import pandas as pd
    from pathlib import Path
    wd_path = Path.cwd()

    # metadata table
    metadata_path = wd_path.joinpath("data")
    metadata_df = pd.read_csv(metadata_path.joinpath("metadata.csv"))

    instruments_dict = get_instruments_dict(get_instruments_list(metadata_df["stems"]))
    print(instruments_dict)
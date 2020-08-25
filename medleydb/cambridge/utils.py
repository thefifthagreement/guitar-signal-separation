# -*- coding: utf-8 -*-
"""
Utilities to use the Cambridge Music Technology audio files
"""
from pathlib import Path
import re

def get_instruments(audio_path: Path) -> list: 
    """
    Return the list of unique instruments names in the files
    """
    instruments = []
    for track in audio_path.glob("**/*.wav"):
        instruments.append(track.name.split(".wav")[0])
    return list(sorted(set(instruments)))

if __name__ == "__main__":
    audio_path = Path("/media/mvitry/7632099B3209620B/Mickaël/Documents/MIR/Cambridge Music Technology/acoustic guitar")
    instruments_list = get_instruments(audio_path)

    print("\nacoustic guitar tracks\n")

    ac_guit_tracks = []
    for track in audio_path.glob("**/*.wav"):
        if re.match(r".*[aA]coustic.*|.*[aA]cGtr.*", track.name.split(".wav")[0]):
            ac_guit_tracks.append([track.parent.name, track.name])

    for t in ac_guit_tracks:
        print(f"{t[0]}: {t[1]}")

    print(len(ac_guit_tracks))
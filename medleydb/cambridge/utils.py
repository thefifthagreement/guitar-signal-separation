# -*- coding: utf-8 -*-
"""
Utilities to use the Cambridge Music Technology audio files
"""
from shutil import copytree
from pathlib import Path
import wave
import array
import re
import scipy.signal
from scipy.io import wavfile
from librosa import load, get_samplerate, get_duration
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from tqdm import tqdm

# data folder for the open-unmix model
umx_data_path = Path("/media/mvitry/Windows/umx/data")

def track_energy(wave, win_len, win):
    """Compute the energy of an audio signal

    Parameters
    ----------
    wave : np.array
        The signal from which to compute energy
    win_len: int
        The number of samples to use in energy computation
    win : np.array
        The windowing function to use in energy computation

    Returns
    -------
    energy : np.array
        Array of track energy

    """
    hop_len = win_len // 2

    wave = np.lib.pad(
        wave, pad_width=(win_len-hop_len, 0), mode='constant', constant_values=0
    )

    # post padding
    wave = librosa.util.fix_length(
        wave, int(win_len * np.ceil(len(wave) / win_len))
    )

    # cut into frames
    wavmat = librosa.util.frame(wave, frame_length=win_len, hop_length=hop_len)

    # Envelope follower
    wavmat = hwr(wavmat) ** 0.5  # half-wave rectification + compression

    return np.mean((wavmat.T * win), axis=1)

def hwr(x):
    """ Half-wave rectification.

    Parameters
    ----------
    x : array-like
        Array to half-wave rectify

    Returns
    -------
    x_hwr : array-like
        Half-wave rectified array

    """
    return (x + np.abs(x)) / 2

def compute_activation_confidence(track_path, win_len=4096, lpf_cutoff=0.075,
                                 theta=0.15, var_lambda=20.0,
                                 amplitude_threshold=0.01):
    """Create the activation confidence annotation for a track. The final
    activation matrix is computed as:
        `C[i, t] = 1 - (1 / (1 + e**(var_lambda * (H[i, t] - theta))))`
    where H[i, t] is the energy of stem `i` at time `t`

    Parameters
    ----------
    track_path : Path
        Path object
    win_len : int, default=4096
        Number of samples in each window
    lpf_cutoff : float, default=0.075
        Lowpass frequency cutoff fraction
    theta : float
        Controls the threshold of activation.
    var_labmda : float
        Controls the slope of the threshold function.
    amplitude_threshold : float
        Energies below this value are set to 0.0

    Returns
    -------
    C : np.array
        Array of activation confidence values shape (n_conf, n_stems)
    """
    H = []

    # MATLAB equivalent to @hanning(win_len)
    win = scipy.signal.windows.hann(win_len + 2)[1:-1]

    audio, rate = librosa.load(track_path, sr=44100, mono=True)
    H.append(track_energy(audio.T, win_len, win))

    # list to numpy array
    H = np.array(H)

    # normalization (to overall energy and # of sources)
    E0 = np.sum(H, axis=0)
    
    H /= np.max(E0)
    # binary thresholding for low overall energy events
    H[:, E0 < amplitude_threshold] = 0.0

    # LP filter
    b, a = scipy.signal.butter(2, lpf_cutoff, 'low')
    H = scipy.signal.filtfilt(b, a, H, axis=1)

    # logistic function to semi-binarize the output; confidence value
    C = 1.0 - (1.0 / (1.0 + np.exp(np.dot(var_lambda, (H - theta)))))

    # add time column
    time = librosa.core.frames_to_time(
        np.arange(C.shape[1]), sr=rate, hop_length=win_len // 2
    )

    # stack time column to matrix
    C_out = np.vstack((time, C))
    return C_out.T

def get_instruments(audio_path: Path) -> list: 
    """
    Return the list of unique instruments names in the files
    """
    instruments = []
    for track in audio_path.glob("**/*.wav"):
        instruments.append(track.name.split(".wav")[0])
    return list(sorted(set(instruments)))

def get_instrument_ratio(activation_path: Path) -> dict:
    """
    Returns a dict {stem: percentage}
    of the ratio of presence of the instrument in the stem

    activation_path: the activation files path
    """
    stem_name = activation_path.name.split('.lab')[0]

    dfx = pd.read_csv(activation_path)
    
    # ratio of the presence of the instrument in the stem
    presence_ratio = (dfx[stem_name] > 0.5).value_counts(True)[1]
    
    return {stem_name: presence_ratio}

def create_activation_files(target_tracks: list) -> list:
    """
    Returns the list of the activation files created

    target_tracks: list of Path to the tracks to annotate
    """
    created_files = []
    print("\nCreating activation files...\n")
    for track in tqdm(target_tracks):
        track_name = track[1].name.split('.wav')[0]
        print(f"{track[0]}: {track_name}")
        activations = compute_activation_confidence(track[1])
        file_name = audio_path.parent.joinpath("annotations", f"{track_name}.lab")
        np.savetxt(
            file_name,
            activations,
            header='time,{}'.format(track_name),
            delimiter=',',
            fmt='%.4f',
            comments=''
            )
        created_files.append(file_name)

    return created_files

def contains_acoustic(track_name: str) -> bool:
    """
    Returns true if the name contains "acoustic guitar"
    """
    return re.match(r".*[aA]coustic.*|.*[aA]cGtr.*", track_name)
    
def get_acoustic_stems(folder: Path) -> list:
    """
    Returns a list of the stems containing acoustic guitar

    folder: a folder containing stems
    """
    ac_guit_stems = []
    for stem in folder.glob("**/*.wav"):
        if contains_acoustic(stem.name.split(".wav")[0]):
            ac_guit_stems.append(stem)
    return ac_guit_stems

def processing_tracks(audio_path: Path, target_instrument_name:str, copy_folders=True, stereo=True) -> dict:
    """
    Returns a dict of the processed tracks

    For each track of the Cambridge Music Technology
    Create a copy of the track to the umx data folder
    The track must contain acoustic guitar and the stems more than 50% of signal
    """
    stems_ratio = {}

    track_folders = [folder for folder in audio_path.iterdir() if folder.is_dir()]

    for folder in track_folders:
        ac_guit_stems = get_acoustic_stems(folder)
        if len(ac_guit_stems) == 0:
            continue
        # for each track, if a stem is more than 60% acoustic guitar
        track_name = folder.name.split("_Full")[0]
        track_stems_ratios = []
        for stem in ac_guit_stems:
            activation_path = audio_path.parent.joinpath("annotations", stem.name.split(".wav")[0] + ".lab")
            ratio = get_instrument_ratio(activation_path)
            track_stems_ratios.append(ratio)
        if len(track_stems_ratios) > 0:
            stems_ratio[track_name] = track_stems_ratios
    
    copied_folders = []
    if copy_folders:
        stems_folder = umx_data_path.joinpath("stems")
        #stems_folder = audio_path.parent.joinpath("stems")
        # create the folder in umx/stems
        print("\nCreating the stems folder")
        for track, stems in tqdm(stems_ratio.items()):
            for i, stem in enumerate(stems):
                # create a copy of the stems
                for stem_name, stem_ratio in stem.items():
                    if stem_ratio < 0.6:
                        continue

                    src_folder = audio_path.joinpath(track + "_Full")
                    dst_folder = stems_folder.joinpath(f"{track}_{i+1}")
                    copytree(src_folder, dst_folder)
                    copied_folders.append(dst_folder)
                    
                    # delete the others acoustic stems
                    for target_stems in stems:
                        for target_stem in target_stems.keys():
                            f = dst_folder.joinpath(f"{target_stem}.wav")
                            # if it's the current stem, rename
                            if target_stem == stem_name:
                                f.rename(dst_folder.joinpath(f"{target_instrument_name}.wav"))
                            # else remove
                            else:
                                f.unlink()  

        # reducing the duration and harmonizing the number of channels and encoding format    
        print("\nReducing the duration...")
        for f in tqdm(copied_folders):
            _, durations = get_stems_durations(f)
            min_duration = np.floor(min(durations))
            for stem in f.glob("**/*.wav"):
                sr = get_samplerate(stem)
                wav, _ = load(stem, sr)
                sf.write(stem, wav[:int(sr*min_duration)], samplerate=44100)
        
        # making stereo files
        if stereo:
            print("making stereo files")
            for f in tqdm(copied_folders):
                for stem in f.glob("**/*.wav"):
                    make_stereo(str(stem), str(stem))

            
    print(f"\n{len(copied_folders)} folders created")
    return stems_ratio 

def get_stems_durations(folder: Path):
    """
    Returns the number of channels and the durations of the stems in the folder
    """
    mono = 0
    durations = []
    for stem in folder.glob("**/*.wav"):
        sr = get_samplerate(stem)
        wav, _ = load(stem, sr, mono=False)
        mono += len(wav.shape)
        durations.append(get_duration(wav, sr))

    return mono / len(durations), durations

def get_folder_stats(audio_path):
    """
    Returns the channels and the durations of the stems
    """ 
    folder_stats = {}
    for folder in tqdm(audio_path.iterdir()):
        if folder.is_dir():
            nb_channels, durations = get_stems_durations(folder)
            if nb_channels == 1:
                channels = "mono"
            elif nb_channels == 2:
                channels = "stéréo"
            else:
                channels = "mixte"

            folder_stats[folder.name] = [channels, min(durations), np.mean(durations)]
    
    return folder_stats

def make_stereo(file1, output):
    """
    Outputs a stereo wav file from the mono input
    """
    ifile = wave.open(file1)

    (nchannels, sampwidth, framerate, nframes, comptype, compname) = ifile.getparams()
    assert comptype == 'NONE'  # Compressed not supported yet
    array_type = {1:'B', 2: 'h', 4: 'l'}[sampwidth]
    left_channel = array.array(array_type, ifile.readframes(nframes))[::nchannels]
    ifile.close()

    stereo = 2 * left_channel
    stereo[0::2] = stereo[1::2] = left_channel

    ofile = wave.open(output, 'w')
    ofile.setparams((2, sampwidth, framerate, nframes, comptype, compname))
    ofile.writeframes(stereo.tobytes())
    ofile.close()

if __name__ == "__main__":
    pass
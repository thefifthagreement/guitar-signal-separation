# -*- coding: utf-8 -*-
"""
Utilities to use the Cambridge Music Technology audio files
"""
from pathlib import Path
import re
import scipy.signal
import numpy as np
import librosa
from tqdm import tqdm

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

if __name__ == "__main__":
    audio_path = Path("/media/mvitry/7632099B3209620B/Mickaël/Documents/MIR/Cambridge Music Technology/acoustic guitar")
    instruments_list = get_instruments(audio_path)

    print("\nacoustic guitar tracks\n")

    ac_guit_tracks = []
    for track in audio_path.glob("**/*.wav"):
        if re.match(r".*[aA]coustic.*|.*[aA]cGtr.*", track.name.split(".wav")[0]):
            ac_guit_tracks.append([track.parent.name, track])

    # création des fichiers d'annotations des pistes acoustic guitar
    print("\nCreating activation files...\n")
    for track in tqdm(ac_guit_tracks):
        track_name = track[1].name.split('.wav')[0]
        print(f"{track[0]}: {track_name}")
        activations = compute_activation_confidence(track[1])
        np.savetxt(
            audio_path.parent.joinpath("annotations", f"{track_name}.lab"),
            activations,
            header='time,{}'.format(track_name),
            delimiter=',',
            fmt='%.4f',
            comments=''
            )
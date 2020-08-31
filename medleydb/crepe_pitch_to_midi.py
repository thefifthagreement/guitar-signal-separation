from os import environ
from pathlib import Path
import crepe
from scipy.io import wavfile
import numpy as np
from librosa.beat import tempo
from librosa import load
from midiutil import MIDIFile

def convert_freq2midi_scalar(f, fA4InHz):

    if f <= 0:
        return 0
    else:
        return (69 + 12 * np.log2(f/fA4InHz))

def ToolFreq2Midi(fInHz, fA4InHz = 440):

    fInHz = np.asarray(fInHz)
    if fInHz.ndim == 0:
       return convert_freq2midi_scalar(fInHz,fA4InHz)

    midi = np.zeros(fInHz.shape)
    for k,f in enumerate(fInHz):
        midi[k] =  convert_freq2midi_scalar(f,fA4InHz)
            
    return (midi)

if __name__ == "__main__":
    
    audio_file = Path(environ["MEDLEYDB_PATH"], "/AClassicEducation_NightOwl/AClassicEducation_NightOwl_STEMS/AClassicEducation_NightOwl_STEM_03.wav")
    audio, sr = load(audio_file, sr=None, mono=True, offset=60, duration=20)
    time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True)

    confidence_list = []

    for i,j in enumerate(confidence) :
            if j > 0.90 :
                confidence_list.append(frequency[i]) 
            else :
                continue

    Freq_midi = (ToolFreq2Midi(confidence_list, fA4InHz=440)).astype(int)
    print(Freq_midi)

    degrees = Freq_midi # MIDI note number
    track = 0
    channel = 0
    time = 0    # In beats
    duration = 1    # In beats
    tempo = tempo   # In BPM
    volume = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                        # automatically)
    MyMIDI.addTempo(track, time, tempo)

    for i, pitch in enumerate(degrees):
        MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

    with open("don't-know1.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)

"""
script to launch a training session of the model
"""
import os
from pathlib import Path
import subprocess
from time import time

umx_train_path = "/path/to/open-unmix-pytorch/repo"
umx_data_path = Path("/path/to/preprocessed/data")

target_instrument = "acoustic_guitar"
target_file = "acoustic_guitar.wav"
model = umx_data_path.joinpath("output")
dataset_type = "trackfolder_var"
root = umx_data_path.joinpath("data")
output = umx_data_path.joinpath("output")
epochs = "200"
batch_size = "32"
seq_dur = "6"
nb_channels = "1"
nb_workers = "4"
ext = ".wav"
seed = "42"

args = [
    "python", "train.py",
    "--target", target_instrument,
    #"--model", str(model), # uncomment to resume training
    "--dataset", dataset_type,
    "--root", str(root),
    "--output", str(output),
    "--epochs", epochs,
    "--batch-size", batch_size,
    "--seq-dur", seq_dur,
    "--nb-workers", nb_workers,
    "--nb-channels", nb_channels,
    "--target-file", target_file,
    "--ext", ext,
    "--seed", seed
]

if __name__ == "__main__":
    os.chdir(umx_train_path)
    start = time()
    subprocess.call(args)
    #print(*args)
    print("\nThe training lasted {:.2f} s".format(time()-start))
import os
from pathlib import Path
import subprocess
from time import time

umx_path = "D:\github\open-unmix-pytorch"

wd_path = Path().cwd()

target_instrument = "clean_electric_guitar"
target_file = "clean_electric_guitar.wav"
model = wd_path.joinpath("output", "19-08-2020_1")
dataset_type = "trackfolder_var"
root = wd_path.joinpath("data")
output = wd_path.joinpath("output", "19-08-2020_1")
epochs = "5"
batch_size = "16"
seq_dur = "6"
nb_workers = "0" # >0 doesn't work on Windows, got to try with Docker (wsl)
ext = ".wav"

args = [
    "python", "train.py",
    "--target", target_instrument,
    #"--model", str(model),
    "--dataset", dataset_type,
    "--root", str(root),
    "--output", str(output),
    "--epochs", epochs,
    "--batch-size", batch_size,
    "--seq-dur", seq_dur,
    "--target-file", target_file,
    "--ext", ext
]

if __name__ == "__main__":
    os.chdir(umx_path)
    start = time()
    #subprocess.call(args)
    print(args)
    print("\nThe training lasted {:.2f} s".format(time()-start))
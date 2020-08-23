import os
from pathlib import Path
import subprocess
from time import time

umx_train_path = "/home/mvitry/Dev/open-unmix-pytorch"
umx_data_path = Path("/media/mvitry/Windows/umx")

target_instrument = "clean_electric_guitar"
target_file = "clean_electric_guitar.wav"
model = umx_data_path.joinpath("output")
dataset_type = "trackfolder_var"
root = umx_data_path.joinpath("data")
output = umx_data_path.joinpath("output")
epochs = "100"
batch_size = "16"
seq_dur = "6"
nb_workers = "4" # >0 doesn't work on Windows, got to try with Docker (wsl)
ext = ".wav"

args = [
    "python", "train.py",
    "--target", target_instrument,
    "--model", str(model),
    "--dataset", dataset_type,
    "--root", str(root),
    "--output", str(output),
    "--epochs", epochs,
    "--batch-size", batch_size,
    "--seq-dur", seq_dur,
    "--nb-workers", nb_workers,
    "--target-file", target_file,
    "--ext", ext
]

if __name__ == "__main__":
    os.chdir(umx_train_path)
    start = time()
    subprocess.call(args)
    #print(*args)
    print("\nThe training lasted {:.2f} s".format(time()-start))
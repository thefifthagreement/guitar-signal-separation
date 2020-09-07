from os import environ
from pathlib import Path
from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from librosa import get_duration, get_samplerate
from scipy.io import wavfile
from test import separate

ALLOWED_EXTENSIONS = {'wav'}

model_name = "/media/mvitry/Windows/umx/output - acg mono - b epoch 332"
target_instrument = "acoustic_guitar"


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = environ['UPLOAD_FOLDER']
app.config['SECRET_KEY'] = environ['SECRET_KEY']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_separate_wav(mix_wav, target_instrument, model_name):
    """
    Returns the separation of the mix
    """
    estimates = separate(audio=mix_wav,
        targets=[target_instrument],
        model_name=model_name,
        device="cuda")

    pred_wav = estimates[target_instrument].squeeze().astype("int16")
    comp_wav = estimates["accompaniment"].squeeze().astype("int16")

    return pred_wav, comp_wav
  
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        # check if the post request has the file part
        if 'mix' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['mix']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            mix_path = Path(app.config['UPLOAD_FOLDER'], filename)
            mix_name = filename.split(".wav")[0] 
            file.save(mix_path)

            duration = get_duration(filename=mix_path)
            sr =  get_samplerate(mix_path)
            metadata = f"{duration}s - {sr}Hz"

            # mix separation
            sr, mix_wav = wavfile.read(mix_path)
            pred_wav, comp_wav = get_separate_wav(mix_wav, target_instrument, model_name)

            pred_path = Path(app.config['UPLOAD_FOLDER'], "{}_{}.wav".format(mix_name, target_instrument))
            comp_path = Path(app.config['UPLOAD_FOLDER'], "{}_comp.wav".format(mix_name))

            wavfile.write(pred_path, sr, pred_wav)
            wavfile.write(comp_path, sr, comp_wav)

            return redirect(url_for('separation', filename=filename, metadata=metadata, pred=pred_path.name, comp=comp_path.name))
    
    return render_template("index.html")

@app.route("/separation/<filename>/<metadata>/<pred>/<comp>")
def separation(filename, metadata, pred, comp):
    return render_template("results.html", filename=filename, metadata=metadata, pred=pred, comp=comp)

if __name__ == '__main__':
    app.run()

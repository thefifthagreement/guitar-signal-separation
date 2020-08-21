# Environnement

Librairies dans le fichier *requirements.txt*
`conda install pytorch=1.3.1 torchvision cudatoolkit=10.1 -c pytorch`

# Paramètres

Pour gérer des pistes avec un nombre de sources différents selon les morceaux: --dataset *trackfolder_var*
Définir un répertoire racine Data, un sous-répertoire "train" et un "valid"
Dans "train" et "valid", créer un répertoire par morceau, ex train dataset: train\1, train\2, valid dataset: valid\1 ...
La cible ("basse", "guitar"...) est désignée nominativement au moment de l'entraînement et donc le STEM associé à la source doit être nommé de la même façon ("basse.wav"...) dans tous les répertoires train et valid

Exemple d'entraînement:

python train.py 
    --target guitar 
    --dataset trackfolder_var 
    --root D:\github\jedha-final-project\open-unmix\data 
    --output D:\github\jedha-final-project\open-unmix\output 
    --epochs 5 
    --target-file guitar.wav 
    --ext .wav

# test du modèle

train set:
- CroqueMadame_Oil_MIX.wav
piano, clean electric guitar, double bass, drum set
- MusicDelta_Shadows_MIX.wav
electric bass, drum set, clean electric guitar, clean electric guitar

test set:
- CroqueMadame_Pilot_MIX.wav
piano, clean electric guitar, double bass, drum set



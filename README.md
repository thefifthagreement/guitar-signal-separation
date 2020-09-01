# Separating the guitar signal from the mix
![alt_text](./static/app_header.png)
## _Music Source Separation application using [Open-Unmix](https://github.com/sigsep/open-unmix-pytorch)_

Jedha Data Science Bootcamp - #dsmft-paris-08 - Fullstack final project

## Introduction

The music source separation is an active research domain and the data-driven methods in this field reaches state of the art performances. The Signal Separation Evalution Campaign (*[SiSec](https://sisec18.unmix.app/#/)*) compares the performance of source separation systems on the same data. The audio signals are those from the _vocals, bass and drums_.

![alt_text](./static/sisec.svg)

In this project, our goal is to separate the _guitar_ signal from the mix.

![alt_text](./static/guitar.svg)

## The MedleyDB dataset

The SiSec is based on the MUSDB dataset where the targets are vocals, bass and drums. You can't use this dataset since the guitar stems are not available.

The [MedleyDB](https://medleydb.weebly.com/) is a dataset of annotated, royalty-free multitrack recordings.

A total of 196 stereo tracks containing the mix, the processed stems, the raw audio and the metadata. The audio format is WAV (44100 Hz, 16 bit)

The clean electric guitar is top 4 while the acoustic is top 9 in the instrument distribution.
![alt_text](./medleydb/images/dist_instrument.png)

30% of the tracks contains clean electric guitar, representing about 4 hours of music.



## References
Open-unmix:
```
Fabian-Robert Stöter, Stefan Uhlich, Antoine Liutkus, Yuki Mitsufuji. Open-Unmix - A Reference Implementation for Music Source Separation. Journal of Open Source Software, Open Journals, 2019, The Journal of Open Source Software, 4 (41), pp.1667. ⟨10.21105/joss.01667⟩. ⟨hal-02293689⟩
```

MedleyDB:
```
R. Bittner, J. Salamon, M. Tierney, M. Mauch, C. Cannam and J. P. Bello, "MedleyDB: A Multitrack Dataset for Annotation-Intensive MIR Research", in 15th International Society for Music Information Retrieval Conference, Taipei, Taiwan, Oct. 2014.
```

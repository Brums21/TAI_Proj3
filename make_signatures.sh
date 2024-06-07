#!/bin/bash

mkdir -p ./song_signatures

for i in ./converted_songs/*.wav
do
    base_name=$(basename "$i" .wav)
    echo $base_name
    ./GetMaxFreqs/bin/GetMaxFreqs -w "song_signatures/${base_name}" "$i"
done
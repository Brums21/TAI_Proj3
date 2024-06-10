#!/bin/bash

SONGS_ANALIZE="./analyze"

for mp3_file in "$SONGS_ANALIZE"/*.mp3; do

    wav_file="$CONVERTED_DIR/$(basename "$mp3_file" .mp3).wav"

    echo "Converting ${wav_file} to .wav format..."
    sox "$mp3_file" -r 44100 "$wav_file"

    base_name=$(basename "$wav_file" .wav)
    echo "Generating signature for ${wav_file}"
    ./GetMaxFreqs/bin/GetMaxFreqs -w "$SONGS_ANALIZE/$base_name" "$wav_file"
done
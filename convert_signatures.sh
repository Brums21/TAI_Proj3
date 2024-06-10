#!/bin/bash

SONGS_DIR="./songs"
CONVERTED_DIR="./converted_songs"
SIGNATURES_DIR="./song_signatures"

mkdir -p "$CONVERTED_DIR" 
mkdir -p "$SIGNATURES_DIR"

rm -rf "$CONVERTED_DIR/*"
rm -rf "$SIGNATURES_DIR/*"

for mp3_file in "$SONGS_DIR"/*.mp3; do
    wav_file="$CONVERTED_DIR/$(basename "$mp3_file" .mp3).wav"
    sox "$mp3_file" -r 44100 "$wav_file"
done

for wav_file in "$CONVERTED_DIR"/*.wav; do
    base_name=$(basename "$wav_file" .wav)
    echo "$base_name"
    ./GetMaxFreqs/bin/GetMaxFreqs -w "$SIGNATURES_DIR/$base_name" "$wav_file"
done

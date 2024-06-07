#!/bin/bash

mkdir -p ./converted_songs

for i in ./songs/*.mp3
do
    sox "$i" -r 44100 "converted_songs/$(basename "$i" .mp3).wav"
done
#!/bin/bash

mkdir -p trim

input_file="converted_songs/Etude Op. 10, no. 12 in C minor - 'Revolutionary'.wav"
output_file=trim/output_segment

start_time=30 
duration=30 

sox "$input_file" "$output_file".wav trim "$start_time" "$duration"
./GetMaxFreqs/bin/GetMaxFreqs -w "${output_file}" "${output_file}.wav"

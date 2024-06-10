#!/bin/bash

INPUT_DIR="./converted_songs"
OUTPUT_DIR="./test_folder"
SIGNATURES_DIR="./test_signatures"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$SIGNATURES_DIR"
rm -rf $OUTPUT_DIR/*
rm -rf $SIGNATURES_DIR/*

percentages=(0.05 0.1 0.2 0.3 0.4 0.5)

for input_file in "$INPUT_DIR"/*.wav
do
    base_name=$(basename "$input_file" .wav)
    echo $base_name
    
    for percentage in "${percentages[@]}"
    do
        
        output_file="${OUTPUT_DIR}/${base_name}_${noise}_${level}_percent.wav"

        total_duration=$(soxi -D "$input_file")
        cut_duration=$(echo "scale=2; $total_duration * $percentage" | bc -l)
        start_time=$(echo "scale=2; ($total_duration - $cut_duration) / 2" | bc -l)

        sox "$input_file" "$output_file".wav trim "$start_time" "$cut_duration"

        signature_file="${SIGNATURES_DIR}/${base_name}_${percentage}_trim"
        ./GetMaxFreqs/bin/GetMaxFreqs -w "$signature_file" "$output_file".wav

        signature_filename=$(basename "$signature_file")

        python3 ./generate_compression.py -gzip -bzip2 -lzma -zstd \
            -folder-test "$SIGNATURES_DIR" \
            -test-file "$signature_filename" \
            -test-start "$start_time" \
            -test-duration "$cut_duration" \
            -test-percentage "$percentage" \
            -csv-file "compression_by_time_of_sample.csv"

        rm -rf $OUTPUT_DIR/*
        rm -rf $SIGNATURES_DIR/*

    done
done

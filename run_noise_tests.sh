#!/bin/bash

INPUT_DIR="./converted_songs"
OUTPUT_DIR="./test_folder"
SIGNATURES_DIR="./test_signatures"
NOISE_LEVELS=(0 0.05 0.10 0.15 0.20)
NOISE_TYPES=("whitenoise" "pinknoise" "brownnoise")

mkdir -p "$OUTPUT_DIR"
mkdir -p "$SIGNATURES_DIR"
rm -rf $OUTPUT_DIR/*
rm -rf $SIGNATURES_DIR/*

for input_file in "$INPUT_DIR"/*.wav
do
    base_name=$(basename "$input_file" .wav)
    echo $base_name
    
    for noise in "${NOISE_TYPES[@]}"
    do
        for level in "${NOISE_LEVELS[@]}"
        do
            output_file="${OUTPUT_DIR}/${base_name}_${noise}_${level}_percent.wav"

            sf1=$(echo "scale=2; 1-$level-0.01" | bc -l)
            sf2=${level}

            sox -m \
            -v $(echo "$(sox "$input_file" -n stat -v 2>&1) * ${sf1}" | bc -l) $input_file \
            -v ${sf2} <(sox "$input_file" -p synth $noise) \
            -b 16 "$output_file"

            start_time=30 
            duration=30 

            temp_file="sox_temp.wav"
            sox "$output_file" "$temp_file" trim "$start_time" "$duration"
            mv "$temp_file" "$output_file"


            signature_file="${SIGNATURES_DIR}/${base_name}_${noise}_${level}_percent"
            ./GetMaxFreqs/bin/GetMaxFreqs -w "$signature_file" "$output_file"

            signature_filename=$(basename "$signature_file")

            python3 ./generate_compression.py -gzip -bzip2 -lzma -zstd \
                -folder-test "$SIGNATURES_DIR" \
                -test-file "$signature_filename" \
                -noise-type "$noise" \
                -noise-percentage "$level" \
                -test-start "$start_time" \
                -test-duration "$duration" \
                -csv-file "compression_by_noise.csv"

            rm -rf $OUTPUT_DIR/*
            rm -rf $SIGNATURES_DIR/*

        done
    done
done

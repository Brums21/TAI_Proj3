#!/bin/bash

INPUT_DIR="./trimmed_songs"

OUTPUT_DIR="./test_folder"
SIGNATURES_DIR="./test_signatures"

NOISE_LEVELS=(0 0.05 0.10 0.15 0.20)
NOISE_TYPES=("whitenoise" "pinknoise" "brownnoise")

mkdir -p "$OUTPUT_DIR"
mkdir -p "$SIGNATURES_DIR"
rm -rf $OUTPUT_DIR/*
rm -rf $SIGNATURES_DIR/*


for input_file in "$INPUT_DIR"/*.mp3
do
    base_name=$(basename "$input_file" .mp3)
    echo $base_name
    
    for noise in "${NOISE_TYPES[@]}"
    do
        for level in "${NOISE_LEVELS[@]}"
        do
           
            converted_song="${SIGNATURES_DIR}/${base_name}.wav"

            output_file="${OUTPUT_DIR}/${base_name}_${noise}_${level}_percent.wav"

            sox "$input_file" -r 44100 "${converted_song}"

            sf1=$(echo "scale=2; 1-$level-0.01" | bc -l)
            sf2=${level}

            sox -m \
            -v $(echo "$(sox "$converted_song" -n stat -v 2>&1) * ${sf1}" | bc -l) $converted_song \
            -v ${sf2} <(sox "$converted_song" -p synth $noise) \
            -b 16 "$output_file"

            total_duration=$(soxi -D "$converted_song")

            signature_file="${SIGNATURES_DIR}/${base_name}_${noise}_${level}_percent"
            ./GetMaxFreqs/bin/GetMaxFreqs -w "$signature_file" "$output_file"

            signature_filename=$(basename "$signature_file")

            python3 ./generate_compression.py -gzip -bzip2 -lzma -zstd \
                -folder-test "$SIGNATURES_DIR" \
                -test-file "$signature_filename" \
                -noise-type "$noise" \
                -noise-percentage "$level" \
                -test-start "0" \
                -test-duration "$total_duration" \
                -csv-file "compression_by_chrom.csv"

            rm -rf $OUTPUT_DIR/*
            rm -rf $SIGNATURES_DIR/*

        done
    done
done
rm -rf $OUTPUT_DIR/
rm -rf $SIGNATURES_DIR/
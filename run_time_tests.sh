#!/bin/bash

INPUT_DIR="./converted_songs"
OUTPUT_DIR="./test_folder"
SIGNATURES_DIR="./test_signatures"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$SIGNATURES_DIR"
rm -rf $OUTPUT_DIR/*
rm -rf $SIGNATURES_DIR/*

TIMES=(3 5 7 10 15 20 30)
PERCENTAGES=(0 0.05 0.10 0.20)

for input_file in "$INPUT_DIR"/*.wav
do
    base_name=$(basename "$input_file" .wav)
    echo $base_name
    
    for time in "${TIMES[@]}"
    do
        for percentage in "${PERCENTAGES[@]}"
        do
            output_file="${OUTPUT_DIR}/${base_name}_${noise}_${percentage}_percent.wav"

            sf1=$(echo "scale=2; 1-$percentage-0.01" | bc -l)
            sf2=${percentage}

            sox -m \
            -v $(echo "$(sox "$input_file" -n stat -v 2>&1) * ${sf1}" | bc -l) $input_file \
            -v ${sf2} <(sox "$input_file" -p synth whitenoise) \
            -b 16 "$output_file"

            total_duration=$(soxi -D "$input_file")
            start_time=$(echo "scale=2; ($total_duration - $time) / 2" | bc -l)  # start in the middle

            temp_file="sox_temp.wav"
            sox "$output_file" "$temp_file" trim "$start_time" "$time"
            mv "$temp_file" "$output_file"

            signature_file="${SIGNATURES_DIR}/${base_name}_${noise}_${percentage}_percent"
            ./GetMaxFreqs/bin/GetMaxFreqs -w "$signature_file" "$output_file"

            signature_filename=$(basename "$signature_file")

            python3 ./generate_compression.py -gzip -bzip2 -lzma -zstd \
                -folder-test "$SIGNATURES_DIR" \
                -test-file "$signature_filename" \
                -noise-type "whitenoise" \
                -noise-percentage "$percentage" \
                -test-start "$start_time" \
                -test-duration "$time" \
                -csv-file "compression_by_time.csv"

            rm -rf $OUTPUT_DIR/*
            rm -rf $SIGNATURES_DIR/*
        done
    done
done

rm -rf $OUTPUT_DIR/
rm -rf $SIGNATURES_DIR/
# TAI 3rd Project - Music Identification using Normalized Compressed Distance

## How to run

### 1. Install libraries

Install sox libraries for song manipulation:

```
sudo apt-get install sox
sudo apt-get install sox libsox-fmt-mp3
```

### 2. Conversion

Convert to .wav, using max frequency rate of 44100Hz and make signatures for the max frequencies registered:

```./convert_signatures.sh```

Note: all dataset songs must be in the `/songs` folder. If no additions or removals to the dataset are made, then this command won't need to be run again.

### 3. Steps to run program

#### 3.1 Install requirements

Create python environment and install the necessary libraries:

```
python3 -m venv venv 
./venv/bin/activate
pip install -r requirements.txt
```

#### 3.1 Run the program

Example usage:

```
./convert_song_to_be_analyzed.sh
python3 ./generate_compression.py -c -gzip -test-file example
```

Note: must specify at least one compression method. Aditionally, the program accepts only the signature of the file to be tested. 

Note 2: It is possible to obtain automatically its signature by placing the .mp3 file in the folder `./analyze`, and running the program `./convert_song_to_be_analyzed.sh`

Accepted parameters:
 - **--compress** or **-c**: Whether to compress the songs or not. This is not needed if all songs are compressed already in the `/compressed` folder.
 - **-gzip**: Whether to compress using gzip.
 - **-bzip2**: Whether to compress using bzip2.
 - **-lzma**: Whether to compress using lzma.
 - **-zstd**: Whether to compress using zstd.
 - **-folder-test**: Folder where the file to be tested is located. Default is `analyze/`.
 - **-test-file**: File to be tested. Default is `signature_test`.
 - **-dataset-signatures**: Folder where the signatures are located. Default is `song_signatures/`.
 - **-dataset-compressions**: "Folder where the compressed signatures are located. Default is `compressed/`

 Parameters used for testing (don't increase functionality):
 - **-noise-type**: Type of noise used.
 - **-noise-percentage**: Percentage of noise used.
 - **-test-start**: Test file start time.
 - **-test-duration**: Test file duration.
 - **-csv-file**: File to write the tests to.

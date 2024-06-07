Install sox library for song manipulation:

```sudo apt-get install sox```

```sudo apt-get install sox libsox-fmt-mp3```

Convert to .wav and use max frequency rate of 44100Hz:

```./convert_and_reduce.sh```

Make signature for the max frequencies registered:

```./make_signatures.sh```

Create python environment and install dependencies:

```python3 -m venv venv```
```source venv/bin/activate```


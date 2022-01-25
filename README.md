Audesc
---------
![Audesc](https://github.com/msalhab96/audesc/blob/main/imgs/logo.jpg)

Audesc is an open-source library for descriptive Audio analysis, using Audesc you can get the following from the audio:
* sampling rate 
* bit width 
* duration
* number of samples 
* number of channels

Installation
==============
### PIP ###

You can install audesc with PIP by using the following command:
```bash
pip install audesc
```

### From Source ###
Clone the following command
```bash
git clone https://github.com/msalhab96/audesc
```
cd to the directory using the following command 
```bash
cd audesc
```
Install the package using the following command
```bash
pip install .
```

Supported Formats
==============
* WAV
* FLAC
* MP3 (Duration not supported yet)

How to Use It 
==============
To describe WAV file
```python
from audesc import WaveDescriber
file_path = 'my/path/to/file.wav'
aud_describer = WaveDescriber(file_path)
description = aud_describer.describe()
print(description)
print(description.sampling_rate)
print(description.channels_count)
print(description.duration)
print(description.bit_rate)
print(description.num_samples)
```

To describe FLAC file
```python
from audesc import FlacDescriber
file_path = 'my/path/to/file.flac'
aud_describer = FlacDescriber(file_path)
description = aud_describer.describe()
print(description)
print(description.sampling_rate)
print(description.channels_count)
print(description.duration)
print(description.bit_rate)
print(description.num_samples)
```

To describe MP3 file
```python
from audesc import MP3Describer
file_path = 'my/path/to/file.mp3'
aud_describer = MP3Describer(file_path)
description = aud_describer.describe()
print(description)
print(description.sampling_rate)
print(description.channels_count)
print(description.duration)   # not supported yet
print(description.bit_rate)
print(description.num_samples)
print(aud_describer.get_mpeg_version())
print(aud_describer.get_layer())
```
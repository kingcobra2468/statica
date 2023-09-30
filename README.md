# Statica

A Python library for converting files to and from their
video representations.

## Features

Some of the features of Statica include:
- Convert files to their video representations and vice versa.

## Video Representation

Statica enables any file to be represented as a video. Each bit
of the input file is encoded, where 1's are black pixels and 0's
are white pixels.

### Pixel Size

Due to compression codecs, data stored as `1x1` pixels might result in
corruption. This is due to information loss, which could shift the pixel
colors around. As a result, Statica allows for variable width/height
pixel sizes, which if set to larger values, will offer protection against
corruption. 

### Sample Frame

Sample frame from the encoded video showing how the file has been encoded. 

<p align="center">
  <kbd><img src="./images/frame.png" width="200" height="350" />
</kbd>
</p>

## Installation

To install and run Statica, follow the following steps:
1. Ensure that `>=Python3.6.9` is installed.
2. Install dependencies with `pip3 install -r requirements.txt`.
3. Build and install Statica with `make clean dist`.

## Running Tests

To run the Pytests, follow the following steps:
1. Run `make clean test`.

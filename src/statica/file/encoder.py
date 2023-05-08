import os

import numpy as np
import cv2
import ffmpeg
import cython

from statica.file.exceptions import InvalidPixelFrameDimensionsError


@cython.cclass
class FileEncoder:
    def __init__(self, in_file, out_file, video_width=720, video_height=1280, fps=30, pixel_width=16, pixel_height=10, buffer_frames=100, is_encrypted=False, is_compressed=False):
        self._in_file = in_file
        self._out_file = out_file
        self._video_width = video_width
        self._video_height = video_height
        self._fps = fps
        self._pixel_width = pixel_width
        self._pixel_height = pixel_height
        self._frame_length = (
            ((video_width // pixel_width) * (video_height // pixel_height)))
        self._buffer_size = buffer_frames * \
            (((video_width // pixel_width) * (video_height // pixel_height)) / 8)
        self._is_encrypted = is_encrypted
        self._is_compressed = is_compressed

        if video_width % pixel_width or video_height % pixel_height:
            raise InvalidPixelFrameDimensionsError(
                video_width, video_height, pixel_width, pixel_height)

        if os.path.exists(self._out_file):
            os.remove(self._out_file)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def encode(self, to_h264=False):
        video = cv2.VideoWriter(self._out_file, cv2.VideoWriter_fourcc(
            *'MP4V'), self._fps, (self._video_width, self._video_height))

        self._set_file_meta(video)

        with open(self._in_file, 'rb') as fd:
            while True:
                byte_list = fd.read(self._buffer_size)
                if not byte_list:
                    break

                z = [(255, 255, 255) if b == 1 else (0, 0, 0) for y in byte_list for b in [
                    y & 1, y >> 1 & 1, y >> 2 & 1, y >> 3 & 1, y >> 4 & 1, y >> 5 & 1, y >> 6 & 1, y >> 7 & 1]]
                arr = np.array(z, dtype=np.uint8)
                del z

                if arr.shape[0] % self._frame_length:
                    arr = np.pad(arr, ((
                        0, self._frame_length - (arr.shape[0] % self._frame_length)), (0, 0)),  'constant')

                arr = arr.repeat(self._pixel_width, axis=0).reshape(-1,
                                                                    arr.shape[0] // self._video_width, self._video_width, 3)
                arr = arr.repeat(self._pixel_height, axis=1)

                arr = arr.reshape(
                    (-1, self._video_height, self._video_width, 3))

                for f in range(arr.shape[0]):
                    video.write(arr[f])

        video.release()

        if to_h264:
            ffmpeg.input(self._out_file).output(f'tmp_{self._out_file}',
                                                vcodec='libx264', pix_fmt='yuv420p').global_args('-an').run(overwrite_output=True)
            os.rename(f'tmp_{self._out_file}', self._out_file)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def _set_file_meta(self, video):
        bit_offset: cython.int
        bit: cython.int
        byte: cython.int

        file_size: cython.int = os.stat(self._in_file).st_size
        file_size_str = bytes(f'{file_size}!', 'ascii')

        frame = self._get_empty_frame()
        ptr_x: cython.int = 0
        ptr_y: cython.int = 0

        for byte in file_size_str:
            for bit_offset in range(8):
                bit = (byte >> bit_offset) & 1

                if ptr_x + self._pixel_width > self._video_width:
                    ptr_x = 0
                    ptr_y += self._pixel_height
                if ptr_y + self._pixel_height > self._video_height:
                    ptr_x, ptr_y = 0, 0
                    video.write(frame)
                    frame = self._get_empty_frame()
                if bit:
                    frame[ptr_y:ptr_y+self._pixel_height,
                          ptr_x:ptr_x+self._pixel_width] = (255, 255, 255)
                ptr_x += self._pixel_width

        video.write(frame)

    def _get_empty_frame(self):
        return np.zeros((self._video_height, self._video_width, 3), np.uint8)

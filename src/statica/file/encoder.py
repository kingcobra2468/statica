import numpy as np
import cv2
import ffmpeg

import os


class FileEncoder:
    def __init__(self, in_file, out_file, video_width=720, video_height=1280, fps=30, pixel_width=16, pixel_height=10, buffer_size=10485760, is_encrypted=False, is_compressed=False):
        self._in_file = in_file
        self._out_file = out_file
        self._video_width = video_width
        self._video_height = video_height
        self._fps = fps
        self._pixel_width = pixel_width
        self._pixel_height = pixel_height
        self._buffer_size = buffer_size
        self._is_encrypted = is_encrypted
        self._is_compressed = is_compressed

    def encode(self, to_h264=False):
        video = cv2.VideoWriter(self._out_file, cv2.VideoWriter_fourcc(
            *'MP4V'), self._fps, (self._video_width, self._video_height))
        frame = self._get_empty_frame()
        ptr_x, ptr_y = 0, 0

        self._set_file_meta(video)

        with open(self._in_file, 'rb') as fd:
            while True:
                byte_list = fd.read(self._buffer_size)
                if not byte_list:
                    break

                for byte in byte_list:
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

        video.release()

        if to_h264:
            ffmpeg.input(self._out_file).output(self._out_file,
                                                vcodec='libx264', pix_fmt='yuv420p').run(overwrite_output=True)

    def _set_file_meta(self, video):
        file_size = os.stat(self._in_file).st_size
        file_size_str = bytes(f'{file_size}!', 'ascii')

        frame = self._get_empty_frame()
        ptr_x, ptr_y = 0, 0

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

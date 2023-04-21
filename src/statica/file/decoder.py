import numpy as np
import cv2


class FileDecoder:
    def __init__(self, in_file, out_file, video_width=720, video_height=1280, pixel_width=16, pixel_height=10, buffer_size=10485760, is_encrypted=False, is_compressed=False):
        self._in_file = in_file
        self._out_file = out_file
        self._video_width = video_width
        self._video_height = video_height
        self._pixel_width = pixel_width
        self._pixel_height = pixel_height
        self._buffer_size = buffer_size
        self._is_encrypted = is_encrypted
        self._is_compressed = is_compressed

    def decode(self):
        video = cv2.VideoCapture(self._in_file)
        file_size = self._get_file_size(video)
        ptr_x, ptr_y = 0, 0

        _, frame = video.read()

        with open(self._out_file, 'wb', buffering=10485760) as fd:
            for num in range(file_size):
                data = 0

                for bit_offset in range(8):
                    if ptr_x + self._pixel_width > self._video_width:
                        ptr_x = 0
                        ptr_y += self._pixel_height
                    if ptr_y + self._pixel_height > self._video_height:
                        ptr_x, ptr_y = 0, 0
                        ret, frame = video.read()

                    bit = 1 if np.average(
                        frame[ptr_y:ptr_y+self._pixel_height, ptr_x:ptr_x+self._pixel_width]) > 125 else 0
                    data = data | (bit << bit_offset)
                    ptr_x += self._pixel_width
                fd.write(bytes([data]))

    def _get_file_size(self, video):
        file_size = ''
        _, frame = video.read()
        ptr_x, ptr_y = 0, 0
        while True:
            byte = 0
            for bit_offset in range(8):
                if ptr_x + self._pixel_width > self._video_width:
                    ptr_x = 0
                    ptr_y += self._pixel_height
                if ptr_y + self._pixel_height > self._video_height:
                    ptr_x, ptr_y = 0, 0
                    # TODO: ability to handle cases where file meta was not extracted
                    ret, frame = video.read()

                bit = 1 if np.average(
                    frame[ptr_y:ptr_y+self._pixel_height, ptr_x:ptr_x+self._pixel_width]) > 125 else 0
                byte = byte | (bit << bit_offset)
                ptr_x += self._pixel_width

            if chr(byte) == '!':
                break

            file_size += chr(byte)

        return int(file_size)

import os

import numpy as np
import cv2
import ffmpeg
import cython

cimport numpy as np


from statica.file.exceptions import InvalidPixelFrameDimensionsError

DTYPE = np.uint8

ctypedef np.uint8_t DTYPE_t


cdef class FileEncoder:
    """FileEncoder encodes a file into video form.
    """
    cdef str _in_file 
    cdef str _out_file
    cdef int _video_width
    cdef int _video_height
    cdef int _fps
    cdef int _pixel_width
    cdef int _pixel_height
    cdef int _buffer_size
    cdef int _is_encrypted
    cdef int _pixels_pw
    cdef int _pixels_ph
    cdef int _is_compressed
    cdef int _frame_length
    
    def __init__(self, in_file, out_file, video_width=720, video_height=1280, fps=30, pixel_width=16, pixel_height=10, buffer_frames=100, is_encrypted=False, is_compressed=False):
        """Constructor.

        Args:
            in_file (str): the path to the input file.
            out_file (str): the path to the output video file.
            video_width (int, optional): the width resolution for the
            output video. Defaults to 720.
            video_height (int, optional): the height resolution for the
            output video. Defaults to 1280.
            fps (int, optional): the output video fps. Defaults to 30.
            pixel_width (int, optional): the pixel width for each data
            bit. Defaults to 16.
            pixel_height (int, optional): the pixel height for each data
            bit. Defaults to 10.
            buffer_frames (int, optional): the number of frames to process
            at each chunk. Defaults to 100.
            is_encrypted (bool, optional): whether to encrypt the output
            data. Defaults to False.
            is_compressed (bool, optional): whether to compress the output
            data. Defaults to False.

        Raises:
            InvalidPixelFrameDimensionsError: thrown if pixel/video frame size are not compatible.
        """
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
            (((video_width // pixel_width) * (video_height // pixel_height)) // 8)
        self._is_encrypted = is_encrypted
        self._is_compressed = is_compressed

        if video_width % pixel_width or video_height % pixel_height:
            raise InvalidPixelFrameDimensionsError(
                video_width, video_height, pixel_width, pixel_height)

        if os.path.exists(self._out_file):
            os.remove(self._out_file)

        if cython.compiled:
            print("Yep, I'm compiled.")
        else:
            print("Just a lowly interpreted script.")

    cpdef void encode(self, to_h264=False):
        """Encodes the input file into its video form.

        Args:
            to_h264 (bool, optional): whether to encode the output video
            in x264 format. Defaults to False.
        """
        video = cv2.VideoWriter(self._out_file, cv2.VideoWriter_fourcc(
            *'MP4V'), self._fps, (self._video_width, self._video_height))

        self._set_file_meta(video)

        with open(self._in_file, 'rb') as fd:
            while True:
                bytes_buffer = fd.read(self._buffer_size)
                # end of file reached
                if not bytes_buffer:
                    break

                # explode each bit (little endian format) in the buffer while setting
                # 1's to black (255, 255, 255) and 0's to white (0, 0, 0)
                bit_buffer = [(255, 255, 255) if b == 1 else (0, 0, 0) for y in bytes_buffer for b in [
                    y & 1, y >> 1 & 1, y >> 2 & 1, y >> 3 & 1, y >> 4 & 1, y >> 5 & 1, y >> 6 & 1, y >> 7 & 1]]
                frames = np.array(bit_buffer, dtype=np.uint8)
                del bit_buffer

                # pad the frames buffer if its not possible to  write n frames of size
                # (width, height, 3). This is needed for the last read buffer chunk since it might
                # be smaller than buffer size.
                if frames.shape[0] % self._frame_length:
                    frames = np.pad(frames, ((
                        0, self._frame_length - (frames.shape[0] % self._frame_length)), (0, 0)),  'constant')

                # explode each bit to have width pixel_width
                frames = frames.repeat(self._pixel_width, axis=0).reshape(-1,
                                                                          frames.shape[0] // self._video_width, self._video_width, 3)
                # explode each bit to have height pixel_height
                frames = frames.repeat(self._pixel_height, axis=1)
                # slice up the frames buffer into individual frames
                frames = frames.reshape(
                    (-1, self._video_height, self._video_width, 3))

                for i in range(frames.shape[0]):
                    video.write(frames[i])

        video.release()

        if to_h264:
            ffmpeg.input(self._out_file).output(f'tmp_{self._out_file}',
                                                vcodec='libx264', pix_fmt='yuv420p').global_args('-an').run(overwrite_output=True)
            os.rename(f'tmp_{self._out_file}', self._out_file)

    cdef void _set_file_meta(self, video):
        """Sets video meta (e.g. input file length) header for decode process.

        Args:
            video (cv2.VideoWriter): the video output stream.
        """
        cdef int bit_offset
        cdef int bit
        cdef int byte
        cdef int file_size
        cdef int ptr_x
        cdef int ptr_y

        file_size = os.stat(self._in_file).st_size
        file_size_str = bytes(f'{file_size}!', 'ascii')

        frame = self._get_empty_frame()
        ptr_x = 0
        ptr_y = 0

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

    cdef np.ndarray _get_empty_frame(self):
        return np.zeros((self._video_height, self._video_width, 3), np.uint8)

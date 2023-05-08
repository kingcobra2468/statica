import skimage.measure
import numpy as np
import cv2
import cython


class FileDecoder:
    """FileDecoder decodes input video into the actual file. 
    """

    def __init__(self, in_file, out_file, video_width=720, video_height=1280, pixel_width=16, pixel_height=10, buffer_size=450, is_encrypted=False, is_compressed=False):
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
            at each chunk. Defaults to 450.
            is_encrypted (bool, optional): whether to encrypt the output
            data. Defaults to False.
            is_compressed (bool, optional): whether to compress the output
            data. Defaults to False.
        """
        self._in_file: str = in_file
        self._out_file: str = out_file
        self._video_width: cython.int = video_width
        self._video_height: cython.int = video_height
        self._pixel_width: cython.int = pixel_width
        self._pixel_height: cython.int = pixel_height
        self._buffer_size: cython.int = buffer_size
        self._is_encrypted: cython.int = is_encrypted
        self._is_compressed: cython.int = is_compressed

    def decode(self):
        """Decodes the input video file into its normal file form.
        """
        video = cv2.VideoCapture(self._in_file)
        file_size: cython.int = self._get_file_size(video)
        buffer = np.zeros((self._buffer_size, self._video_height,
                          self._video_width, 3), dtype=np.uint)
        actual_frames = 0

        with open(self._out_file, 'wb', buffering=10485760) as fd:
            while True:
                actual_frames = 0
                # take in a buffer of at most buffer_size frames
                for i in range(self._buffer_size):
                    status, frame = video.read()
                    if not status:
                        break

                    actual_frames += 1
                    buffer[i] = frame

                if not actual_frames:
                    break

                # merge all frames into a single buffer
                frames = buffer[:actual_frames].reshape(
                    (-1, self._video_width, 3))
                # apply average pooling with kernel (pixel_height, pixel_width) to determine
                # pixel color
                frames = skimage.measure.block_reduce(
                    frames, (self._pixel_height, self._pixel_width, 3), np.mean)
                # determine if pixel is a 1 (average above 125) or 0 (below 125)
                frames = np.array(
                    [1 if a > 125 else 0 for a in frames.astype(np.uint8).reshape((-1, 1))])
                # reshape buffer into binary form of each byte
                frames = frames.reshape((-1, 8))
                # convert to bytes
                frames = np.packbits(frames, bitorder='little').tobytes()

                # check if last chunk has been processed
                if file_size - len(frames) < 0:
                    fd.write(frames[:file_size])
                    break

                fd.write(frames)
                # number of bytes left to read
                file_size -= len(frames)

    def _get_file_size(self, video):
        """Retrieves the file size from the video meta.

        Args:
            video (cv2.VideoWriter): the video input stream.

        Returns:
            int: the output file size.
        """
        file_size: str = ''
        _, frame = video.read()
        ptr_x: cython.int = 0
        ptr_y: cython.int = 0

        while True:
            byte = 0
            for bit_offset in range(8):
                if ptr_x + self._pixel_width > self._video_width:
                    ptr_x = 0
                    ptr_y += self._pixel_height
                if ptr_y + self._pixel_height > self._video_height:
                    ptr_x, ptr_y = 0, 0
                    # TODO: ability to handle cases where file meta was not extracted
                    _, frame = video.read()

                bit = 1 if np.average(
                    frame[ptr_y:ptr_y+self._pixel_height, ptr_x:ptr_x+self._pixel_width]) > 125 else 0
                byte = byte | (bit << bit_offset)
                ptr_x += self._pixel_width

            if chr(byte) == '!':
                break

            file_size += chr(byte)

        return int(file_size)

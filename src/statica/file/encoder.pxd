cimport numpy as np

ctypedef np.uint8_t DTYPE_t


cdef class FileEncoder:
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

    cpdef void encode(self, int to_h264=*)
    cdef void _set_file_meta(self, video)
    cdef np.ndarray _get_empty_frame(self)

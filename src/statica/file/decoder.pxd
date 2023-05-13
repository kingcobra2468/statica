cdef class FileDecoder:
    cdef str _in_file 
    cdef str _out_file
    cdef int _video_width
    cdef int _video_height
    cdef int _fps
    cdef int _pixel_width
    cdef int _pixel_height
    cdef int _buffer_size
    cdef int _is_encrypted
    cdef int _is_compressed

    cpdef void decode(self)
    cdef int _get_file_size(self, video)
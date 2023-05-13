class InvalidPixelFrameDimensionsError(ValueError):
    def __init__(self, video_width, video_height, pixel_width, pixel_height):
        super().__init__(
            f'Invalid pixel shape ({pixel_width}, {pixel_height}) for frame shape({video_width},{video_height})')

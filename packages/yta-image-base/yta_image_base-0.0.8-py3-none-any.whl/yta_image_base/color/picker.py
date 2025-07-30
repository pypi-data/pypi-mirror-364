from yta_image_base.parser import ImageParser
from collections import Counter
from PIL import Image
from typing import Union

import numpy as np


# TODO: Maybe move this to another place
# TODO: Refactor to check if 'pixel' attribute
# has a len of 3 (rgb) or 4 (rgba) values.
class PixelFilterFunction:
    """
    Class to interact with image pixels and detect greens or transparent
    pixels to be used in, for example, ImageRegionFinder functionality.
    """

    @staticmethod
    def is_green(
        pixel: list[int, int, int]
    ):
        """
        Check if the provided 'pixel' is a blue pixel,
        which means that color is in the [100, 255] range
        while the others are in the [0, 100] range.
        """
        # TODO: Validate 'pixel' parameter
        r, g, b = pixel

        return (
            0 <= r <= 100 and
            100 <= g <= 255 and
            0 <= b <= 100
        )
    
    @staticmethod
    def is_blue(
        pixel: list[int, int, int]
    ):
        """
        Check if the provided 'pixel' is a blue pixel,
        which means that color is in the [100, 255] range
        while the others are in the [0, 100] range.
        """
        # TODO: Validate 'pixel' parameter
        r, g, b = pixel

        return (
            0 <= r <= 100 and
            0 <= g <= 100 and
            100 <= b <= 255
        )
    
    @staticmethod
    def is_red(
        pixel: list[int, int, int]
    ):
        """
        Check if the provided 'pixel' is a blue pixel,
        which means that color is in the [100, 255] range
        while the others are in the [0, 100] range.
        """
        # TODO: Validate 'pixel' parameter
        r, g, b = pixel

        return (
            100 <= r <= 255 and
            0 <= g <= 100 and
            0 <= b <= 100
        )
    
    @staticmethod
    def is_transparent(
        pixel: list[int, int, int, int]
    ):
        """
        Checks if the alpha channel (4th in array) is set
        to 0 (transparent). The pixel must be obtained from
        a RGBA image (so 4 dimentions available).
        """
        # TODO: Validate 'pixel' parameter
        _, _, _, a = pixel

        return a == 0

class ColorPicker:
    """
    Class to encapsulate and simplify the functionality related to
    image color detection.
    """

    @staticmethod
    def get_most_common_green_rgb_color(
        image: Union[str, Image.Image, np.ndarray]
    ):
        """
        Returns the most common (dominant) rgb color in a 
        (r, g, b) format.
        """
        image = ImageParser.to_pillow(image)

        return ColorPicker.get_dominant_color(image, PixelFilterFunction.is_green)

    @staticmethod
    def get_most_common_green_rgb_color_and_similars(
        image: Union[str, Image.Image, np.ndarray]
    ):
        """
        Returns the most common rgb color and its similar colors
        found in the provided 'image_filename' as a pair of values
        (most_common, similars). Extract them as a pair.
        """
        image = ImageParser.to_pillow(image)

        return ColorPicker.get_dominant_and_similar_colors(image, PixelFilterFunction.is_green, _is_similar_green)

    @staticmethod
    def get_dominant_color(
        image: Union[str, Image.Image, np.ndarray],
        pixel_filter_function: PixelFilterFunction = None
    ):
        """
        Opens the provided 'image_filename' and gets the dominant
        color applying the 'pixel_filter_function' if provided.
        """
        image = ImageParser.to_pillow(image)

        return _get_dominant_color(image, pixel_filter_function)[0]

    @staticmethod
    def get_dominant_and_similar_colors(
        image: Union[str, Image.Image, np.ndarray],
        pixel_filter_function: PixelFilterFunction = None,
        similarity_function = None
    ):
        """
        Opens the provided 'image_filename', gets the dominant
        color and also the similar ones by applying the 
        'pixel_filter_function' if provided.
        """
        image = ImageParser.to_pillow(image)

        return _get_dominant_color(image, pixel_filter_function, similarity_function)



def _is_similar_green(
    color1,
    color2,
    tolerance: float = 30
):
    tolerance = (
        30
        if not tolerance else
        tolerance
    )

    # TODO: This below should be comparing 
    return (
        abs(color1[0] - color2[0]) <= tolerance * 0.5 and
        abs(color1[1] - color2[1]) <= tolerance * 2 and
        abs(color1[2] - color2[2]) <= tolerance * 0.5
    )

def _get_dominant_color(
    image: Union[str, Image.Image, np.ndarray],
    pixel_filter_function: PixelFilterFunction = None,
    similarity_function = None
):
    image = ImageParser.to_pillow(image)
    
    pixels = list(image.getdata())
    if pixel_filter_function is not None:
        pixels = [
            pixel
            for pixel in pixels
            if pixel_filter_function(pixel)
        ]

    color_count = Counter(pixels)

    if not color_count:
        return None, None

    dominant_color = color_count.most_common(1)[0][0] #[0][1] is the 'times'

    if similarity_function is None:
        return dominant_color, None

    similar_colors = [
        color
        for color in color_count.keys()
        if (
            similarity_function(color, dominant_color, 30) and
            color != dominant_color
        )
    ]
    
    return dominant_color, similar_colors

# TODO: Maybe make this methods work with numpy arrays (?)
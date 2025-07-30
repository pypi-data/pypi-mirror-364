"""
Image edition module.

Interesting links below:
- https://www.geeksforgeeks.org/image-enhancement-techniques-using-opencv-python/
- https://www.geeksforgeeks.org/changing-the-contrast-and-brightness-of-an-image-using-python-opencv/

TODO: Maybe move to a 'yta_image_editor' lib (?)
"""
from yta_image_base.editor.utils import change_image_brightness, change_image_color_hue, change_image_color_temperature, change_image_contrast, change_image_sharpness, change_image_white_balance
from yta_image_base.parser import ImageParser
from yta_constants.enum import YTAEnum as Enum
from PIL import Image
from typing import Union

import cv2
import numpy as np


class LutTable(Enum):
    """
    Image LUT tables definition to be able to handle them
    and apply to images to modify those images.

    You create a table in which you set the new values
    for all the 256 pixels so the previous 0 will be
    other number (or maybe 0 in that case).
    """

    INVERSE = 'inverse'
    SQUARE_ROOT = 'square_root'
    CUBE = 'cube'

    def get_lut_table(
        self
    ):
        """
        Obtain the LUT table array, which is a 2D table with 256
        indexes containing the pixel color in which the original
        color must be converted.
        """
        functions = {
            LutTable.INVERSE: lambda pixel: 255 - pixel,
            LutTable.SQUARE_ROOT: lambda pixel: (pixel * 255) ** (1 / 2),
            LutTable.CUBE: lambda pixel: (pixel ** 3) / (255 ** 2)
        }

        return np.array([
            functions[self](i)
            for i in range(256)
        ], dtype = np.uint8)
        
    def apply_to_image(
        self,
        image: any
    ) -> np.ndarray:
        """
        Apply the lut table to the provided image.

        Result is a numpy array in RGB format.
        """
        # Result is GBR format, transform to RGB
        return cv2.LUT(ImageParser.to_opencv(image), self.get_lut_table())[:, :, ::-1]
    
class _Color:
    """
    Class to handle the color variations of an
    image when inside an ImageEditor instance.
    """
    def __init__(
        self,
        editor: 'ImageEditor'
    ):
        self.editor: ImageEditor = editor
        """
        The ImageEditor instance this _Color instance
        belongs to.
        """

    def temperature(
        self,
        factor: int = 0
    ) -> 'ImageEditor':
        """
        Set the color temperature of the image.

        Limits of the 'factor' attribute:
        - `[-50, 50]`
        """
        self.editor.image = change_image_color_temperature(self.editor.image, factor)

        return self.editor
    
    def hue(
        self,
        factor: int = 0
    ) -> 'ImageEditor':
        """
        Set the color hue of the image.

        Limits of the 'factor' attribute:
        - `[-50, 50]`
        """
        self.editor.image = change_image_color_hue(self.editor.image, factor)

        return self.editor
    
    def brightness(
        self,
        factor: int = 0
    ) -> 'ImageEditor':
        """
        Set the color brightness of the image.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        self.editor.image = change_image_brightness(self.editor.image, factor)

        return self.editor
    
    def contrast(
        self,
        factor: int = 0
    ) -> 'ImageEditor':
        """
        Set the color contrast of the image.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        self.editor.image = change_image_contrast(self.editor.image, factor)

        return self.editor

    def sharpness(
        self,
        factor: int = 0
    ) -> 'ImageEditor':
        """
        Set the color sharpness of the image.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        self.editor.image = change_image_sharpness(self.editor.image, factor)

        return self.editor

    def white_balance(
        self,
        factor: int = 0
    ) -> 'ImageEditor':
        """
        Set the color white_balance of the image.

        Limits of the 'factor' attribute:
        - `????`
        """
        self.editor.image = change_image_white_balance(self.editor.image, factor)

        return self.editor

class ImageEditor:
    """
    Class to simplify and encapsulate all the functionality
    related to image edition.

    Example of usage:
    - `ImageEditor(image).color.temperature(33)` - will set
    the color temperature of the image to 33, modifying the
    image in the instance.
    - `ImageEditor(image).apply_lut(lut_table)` - will apply
    the 'lut_table' provided to the image.
    """
        
    @property
    def color(
        self
    ):
        """
        The properties related to color we can change.
        """
        return self._color

    def __init__(
        self,
        image: Union[str, Image.Image, np.ndarray]
    ):
        self.original_image: Union[str, Image.Image, np.ndarray] = image
        """
        The image we are editing, stored as it was received.
        """
        # TODO: .copy() (?)
        self.image: np.ndarray = image
        """
        The image that is being edited with all the 
        modifications we have done, that will always
        be a numpy array.
        """
        # The modifiers below
        self._color: _Color = _Color(self)
    
    def apply_lut(
        self,
        lut_table: LutTable
    ) -> 'ImageEditor':
        """
        Apply the 2D Lut table provided in the 'lut_table'
        parameter to the also given 'image'.

        Thanks to:
        - https://gist.github.com/blroot/b22abc23526af2711d92cc3b3f13b907
        """
        lut_table = LutTable.to_enum(lut_table)

        self.image = lut_table.apply_to_image(self.image)

        return self
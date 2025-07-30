from yta_image_base.parser import ImageParser
# TODO: I should move this from 'yta_video_utils'
# to a more general utils library...
from yta_video_utils.resize import get_cropping_points_to_keep_aspect_ratio
from yta_constants.file import FileExtension, FileParsingMethod
from yta_programming.output import Output
from yta_general.dataclasses import FileReturned
from PIL import Image
from typing import Union

import cv2


class ImageResizer:
    """
    Class to resize images.
    """

    @staticmethod
    def resize(
        image: Union[str, any],
        size: tuple[int, int],
        output_filename: Union[str, None] = None
    ) -> FileReturned:
        """
        Resizes the image to the provided 'size' by cropping a
        region of the given 'image' that fits the 'size' aspect
        ratio and resizing that region to the 'size'.

        This method is using the whole image and then resizing,
        so the quality of the image is preserved and no small
        regions are used. The most part of the image is 
        preserved.

        This method returns the image modified.

        This method will write the image if 'output_filename' is
        provided.
        """
        image = ImageParser.to_pillow(image)

        # TODO: Maybe move the method to another library (?)
        top_left, bottom_right = get_cropping_points_to_keep_aspect_ratio(image.size, size)
        image = image.crop((top_left[0], top_left[1], bottom_right[0], bottom_right[1]))
        image = image.resize(size)

        if output_filename is not None:
            output_filename = Output.get_filename(output_filename, FileExtension.PNG)
            image.save(output_filename)

        return FileReturned(
            content = image,
            filename = None,
            output_filename = output_filename,
            type = None,
            is_parsed = True,
            parsing_method = FileParsingMethod.PILLOW_IMAGE,
            extra_args = None
        )


# TODO: This below is so raw... remove if
# no longer used and replaceable with others
def resize_scaling(image_filename, width, height, output_filename = None):
    """
    Resizes the provided 'image_filename' to the provided 'width' and 'height' keeping the
    aspect ratio. This method enlarges the image to fit the desired size and then makes a 
    crop to obtain that size from the center of the resized image. If 'output_filename' is
    provided, the image is saved locally with that name.
    """
    image = Image.open(image_filename)
    image_width, image_height = image.size

    if image_width == width and image_height == height:
        return image.save(output_filename)

    aspect_ratio = image_width / image_height
    if aspect_ratio > (width / height):
        # Image is very horizontal, so width changes faster, we need to focus on height
        factor = (height * 100 / image_height) / 100
        image_width = int(image_width * factor)
        image_height = height
    else:
        # Image is very vertical, so height changes faster, we need to focus on width
        factor = (width * 100 / image_width) / 100
        image_width = 1920
        image_height = int(image_height * factor)
    image = image.resize((image_width, image_height))

    # We will crop form the center to edges
    left = 0
    right = width
    top = 0
    bottom = height
    if image_width > width:
        # If it is 1960 => leave [0, 20], get [20, 1940], leave [1940, 1960]
        margin = int((image_width - width) / 2)
        left = 0 + margin
        right = image_width - margin
        # We make and adjustment if some pixel left
        while (right - left) > width:
            right -= 1
        while (right - left) < width:
            if left > 0:
                left -= 1
            else:
                right += 1
    if image_height > height:
        # If it is 1140 => leave [0, 30], get [30, 1110], leave [1110, 1140]
        margin = int((image_height - height) / 2)
        top = 0 + margin
        bottom = image_height - margin
        # We make and adjustment if some pixel left
        while (bottom - top) > height:
            bottom -= 1
        while (bottom - top) < height:
            if top > 0:
                top -= 1
            else:
                bottom += 1

    image = image.crop((left, top, right, bottom))
    # Image that is 1920x1080 and is the center of the original image
    if output_filename:
        image.save(output_filename)

    return image

def resize_without_scaling(image_filename, width = 1920, height = 1080):
    """
    This method gets an image, resizes it and overwrites the original one.

    TODO: This method need work.
    """
    # TODO: We resize it simply, we don't care about scale
    image = cv2.imread(image_filename)
    resized_image = cv2.resize(image, dsize = (width, height), interpolation = cv2.INTER_CUBIC)
    cv2.imwrite(image_filename, resized_image)

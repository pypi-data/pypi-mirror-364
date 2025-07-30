from yta_image_base.parser import ImageParser
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator
from yta_constants.image import COLOR_TEMPERATURE_CHANGE_LIMIT, COLOR_HUE_CHANGE_LIMIT, CONTRAST_LIMIT, SHARPNESS_LIMIT, BRIGHTNESS_LIMIT
from PIL import Image, ImageEnhance

import cv2
import numpy as np
import colorsys


def change_image_color_temperature(
    image: any,
    factor: int = 0
) -> np.ndarray:
    """
    Change the 'image' color temperature by the
    provided 'factor', that must be a value between
    [-50, 50].

    The color change consist of updating the red and
    blue values, where red is calid and blue is cold.
    Increasing the temperature means increasing the
    red color, and decreasing it, decreasing the blue
    color.
    """
    ParameterValidator.validate_mandatory_number_between('factor', factor, COLOR_TEMPERATURE_CHANGE_LIMIT[0], COLOR_TEMPERATURE_CHANGE_LIMIT[1])
    
    # The '.copy()' makes it writeable
    image = ImageParser.to_numpy(image).copy()

    if factor == 0:
        return image

    # We want the factor being actually a value between 0.50 and 1.50,
    # but multiplying by 1.5 is equal to divide by 0.75 so I need to
    # manually do this calculation to apply the formula correctly
    factor = 1 - (0.25 - _normalize(factor, COLOR_TEMPERATURE_CHANGE_LIMIT[0], 0, 0, 0.25)) if factor < 0 else 1 + _normalize(factor, 0, COLOR_TEMPERATURE_CHANGE_LIMIT[1], 0, 0.5)
    
    r, b = image[:, :, 0], image[:, :, 2]
    
    # Min and max values are 0 and 255
    r = np.clip(r * factor, 0, 255)
    b = np.clip(b / factor, 0, 255)
    
    # Reconstruimos la imagen con los canales modificados
    image[:, :, 0] = r
    image[:, :, 2] = b

    return image

# These below are 2 functions to convert
# TODO: Please, move these functions to a method
# maybe in 'yta_general_utils' or in 'yta_multimedia'
rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

def change_image_color_hue(
    image: any,
    factor: int = 0
) -> np.ndarray:
    """
    Change the 'image' color hue by the provided
    'factor', that must be a value between [-50, 50].

    Colorize PIL image `original` with the given
    `factor` (hue within 0-360); returns another PIL image.
    """
    ParameterValidator.validate_mandatory_number_between('factor', factor, COLOR_HUE_CHANGE_LIMIT[0], COLOR_HUE_CHANGE_LIMIT[1])
    
    # The '.copy()' makes it writeable
    image = ImageParser.to_numpy(image).copy()

    factor = _normalize(factor, COLOR_HUE_CHANGE_LIMIT[0], COLOR_HUE_CHANGE_LIMIT[1], 0, 360)
    
    # TODO: This code is not working well
    # TODO: This method is very very slow
    #arr = np.array(np.asarray(img).astype('float'))
    #r, g, b, a = np.rollaxis(image, axis = -1)
    print(image.size) # size is 6220800
    r, g, b = np.rollaxis(image, axis = -1)
    #r, g, b = np.moveaxis(image, -1, 0)
    h, s, v = rgb_to_hsv(r, g, b)
    h = factor / 360.0
    r, g, b = hsv_to_rgb(h, s, v)
    #arr = np.dstack((r, g, b, a))
    arr = np.dstack((r, g, b)).astype(np.uint8)
    print(arr.size) # size is 220800
    print(arr)

    # TODO: I don't like this line below
    return arr
    return Image.fromarray(arr.astype('uint8'), 'RGBA')

def change_image_brightness(
    image: any,
    factor: int = 0
) -> np.ndarray:
    """
    Change the 'image' brightness by the provided
    'factor', that must be a value between [-100, 100].
    """
    ParameterValidator.validate_mandatory_number_between('factor', factor, BRIGHTNESS_LIMIT[0], BRIGHTNESS_LIMIT[1])
    
    image = ImageParser.to_pillow(image).copy()

    # factor from -100 to 0 must be from 0.5 to 1
    # factor from 0 to 100 must be from 1 to 2
    factor = _normalize(factor, BRIGHTNESS_LIMIT[0], 0, 0.5, 1.0) if factor <= 0 else _normalize(factor, 0, BRIGHTNESS_LIMIT[1], 1.0, 2.0)

    image = ImageEnhance.Brightness(image).enhance(factor)

    return ImageParser.to_numpy(image)

def change_image_contrast(
    image: any,
    factor: int = 0
) -> np.ndarray:
    """
    Change the 'image' contrast by the provided
    'factor', that must be a value between [-100, 100].
    """
    ParameterValidator.validate_mandatory_number_between('factor', factor, CONTRAST_LIMIT[0], CONTRAST_LIMIT[1])
    
    image = ImageParser.to_pillow(image).copy()

    # factor from -100 to 0 must be from 0.5 to 1
    # factor from 0 to 100 must be from 1 to 2
    factor = _normalize(factor, CONTRAST_LIMIT[0], 0, 0.5, 1.0) if factor <= 0 else _normalize(factor, 0, CONTRAST_LIMIT[1], 1.0, 2.0)

    image = ImageEnhance.Contrast(image).enhance(factor)

    return ImageParser.to_numpy(image)

def change_image_sharpness(
    image: any,
    factor: int = 0
) -> np.ndarray:
    """
    Change the 'image' sharpness by the provided
    'factor', that must be a value between [-100, 100].

    A factor of -100 gives you a blurred image while
    a factor of 100 gives you a sharped image.
    """
    ParameterValidator.validate_mandatory_number_between('factor', factor, SHARPNESS_LIMIT[0], SHARPNESS_LIMIT[1])

    image = ImageParser.to_pillow(image).copy()
    
    # factor from -100 to 0 must be from 0.5 to 1
    # factor from 0 to 100 must be from 1 to 2
    factor = _normalize(factor, SHARPNESS_LIMIT[0], 0, 0.0, 1.0) if factor <= 0 else _normalize(factor, 0, SHARPNESS_LIMIT[1], 1.0, 2.0)

    image = ImageEnhance.Sharpness(image).enhance(factor)

    return ImageParser.to_numpy(image)

def change_image_white_balance(
    image: any,
    factor: int = 0
) -> np.ndarray:
    """
    TODO: Explain
    
    The result is in RGB format.
    """
    # TODO: I'm not using the 'factor'
    # TODO: I have a factor limit setting for this
    
    # TODO: Apply factor -> 0.0 means no change
    image = ImageParser.to_opencv(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    # Average of green channel
    avg_a = np.average(image[:, :, 1])
    # Average of red channel
    avg_b = np.average(image[:, :, 2])
    image[:, :, 1] = image[:, :, 1] - ((avg_a - 128) * (image[:, :, 0] / 255.0) * 1.2)
    image[:, :, 2] = image[:, :, 2] - ((avg_b - 128) * (image[:, :, 0] / 255.0) * 1.2)

    balanced_image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

    return balanced_image

# TODO: I have a new Value_normalizer class to handle normalization
# so this has to be avoided and use that general function instead
def _normalize(
    number: float,
    input_lower_limit: float,
    input_upper_limit: float,
    output_lower_limit: float = 0.0,
    output_upper_limit: float = 1.0
):
    """
    Normalize the 'number' value to be between 'output_lower_limit'
    and 'output_upper_limit', according to the input provided, that
    is between the 'input_lower_limit' and 'input_upper_limit' 
    values.
    """
    # TODO: Refactor these limits below
    if not NumberValidator.is_number(number) or not NumberValidator.is_number(input_lower_limit) or not NumberValidator.is_number(input_upper_limit) or not NumberValidator.is_number(output_lower_limit) or not NumberValidator.is_number(output_upper_limit):
        raise Exception('All the parameters must be numbers.')

    ParameterValidator.validate_mandatory_number_between('number', number, input_lower_limit, input_upper_limit)

    if input_upper_limit <= input_lower_limit or output_upper_limit <= output_lower_limit:
        raise Exception('The upper limit must be greater than the lower limit.')
    
    return (number - input_lower_limit) / (input_upper_limit - input_lower_limit) * (output_upper_limit - output_lower_limit) + output_lower_limit
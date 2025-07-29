from yta_constants.video import ZOOM_LIMIT, ROTATION_LIMIT, COLOR_TEMPERATURE_LIMIT
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_validation.parameter import ParameterValidator
from yta_validation.number import NumberValidator
from yta_validation import PythonValidator


# TODO: This must be maybe moved to another file
# because it is mixed with the 'subclip_video'
# method...
def _validate_is_video_attribute_modifier_instance(
    element: 'SubClipAttributeModifier'
):
    ParameterValidator.validate_mandatory_instance_of('element', element, 'SubClipAttributeModifier')
    
def _validate_zoom(
    zoom: int
):
    ParameterValidator.validate_mandatory_number_between('zoom', zoom, ZOOM_LIMIT[0], ZOOM_LIMIT[1])
    
def _validate_x_movement(
    x_movement: int
):
    ParameterValidator.validate_mandatory_number_between('x_movement', x_movement, -DEFAULT_SCENE_SIZE[0] * 4, DEFAULT_SCENE_SIZE[0] * 4)
    
def _validate_y_movement(
    y_movement: int
):
    ParameterValidator.validate_mandatory_number_between('y_movement', y_movement, -DEFAULT_SCENE_SIZE[0] * 4, DEFAULT_SCENE_SIZE[0] * 4)

def _validate_rotation(
    rotation: int
):
    ParameterValidator.validate_mandatory_number_between('rotation', rotation, ROTATION_LIMIT[0], ROTATION_LIMIT[1])

def _validate_setting(
    setting: 'SubClipSetting',
    name: str,
    range: tuple[float, float]
):
    ParameterValidator.validate_mandatory_instance_of('setting', setting, 'SubClipSetting')
    ParameterValidator.validate_mandatory_number_between('setting.initial_value', setting.initial_value, range[0], range[1])
    ParameterValidator.validate_mandatory_number_between('setting.final_value', setting.final_value, range[0], range[1])

def _validate_attribute_modifier(
    attribute_modifier: 'SubClipAttributeModifier',
    name: str,
    limit_range: tuple[float, float],
    number_of_frames: int
):
    """
    Validate the provided 'attribute_modifier' according to
    the given 'limit_range' in which all the values must fit.
    Also, if it is a Graphic instance, the 'number_of_frames'
    will be used to generate the values and check them.
    """
    ParameterValidator.validate_mandatory_instance_of('attribute_modified', attribute_modifier, 'SubClipAttributeModifier')
    
    if PythonValidator.is_list(attribute_modifier.modifier):
        # TODO: Validate all values
        if any(not NumberValidator.is_number_between(value, limit_range[0], limit_range[1]) for value in attribute_modifier.modifier):
            raise Exception(f'The parameter "{name}" provided has at least one value out of the limits [{limit_range[0]}, {limit_range[1]}]')
    elif PythonValidator.is_instance(attribute_modifier.modifier, 'SubClipSetting'):
        if not NumberValidator.is_number_between(attribute_modifier.modifier.initial_value, limit_range[0], limit_range[1]):
            raise Exception(f'The parameter "{name}" provided "initial_value" is not a number between [{limit_range[0]}, {limit_range[1]}].')
        
        if not NumberValidator.is_number_between(attribute_modifier.modifier.final_value, limit_range[0], limit_range[1]):
            raise Exception(f'The parameter "{name}" provided "final_value" is not a number between [{limit_range[0]}, {limit_range[1]}].')
    elif PythonValidator.is_instance(attribute_modifier.modifier, 'Graphic'):
        # TODO: This is very agressive, according to the way
        # we join the pairs of nodes we could get outliers
        # that are obviously out of the limit range. Some
        # easing functions have values below 0 and over 1.
        if any(not NumberValidator.is_number_between(value, limit_range[0], limit_range[1]) for value in attribute_modifier.get_values(number_of_frames)):
            raise Exception(f'The parameter "{name}" provided has at least one value out of the limits [{limit_range[0]}, {limit_range[1]}]')
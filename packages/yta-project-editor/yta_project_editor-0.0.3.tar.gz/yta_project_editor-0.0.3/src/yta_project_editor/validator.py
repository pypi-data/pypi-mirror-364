from yta_project_editor.settings import TRACKS_INDEXES_LIMIT, MINIMUM_DIMENSIONS, MAXIMUM_DIMENSIONS, MINIMUM_FPS, MAXIMUM_FPS
from yta_validation.parameter import ParameterValidator


class ProjectEditorValidator:
    """
    Class to wrap validation functionality.
    """

    @staticmethod
    def validate_layer_index(
        layer_index: int
    ) -> None:
        """
        Check that the 'layer_index' provided is a
        valid value according to our settings or
        raise an exception if invalid.
        """
        ParameterValidator.validate_mandatory_number_between('layer_index', layer_index, TRACKS_INDEXES_LIMIT[0], TRACKS_INDEXES_LIMIT[1])

    @staticmethod
    def validate_width(
        width: int
    ) -> None:
        """
        Check that the 'width' provided is valid
        according to our settings, or raise an
        exception if invalid.
        """
        ParameterValidator.validate_mandatory_number_between('width', width, MINIMUM_DIMENSIONS[0], MAXIMUM_DIMENSIONS[0])

    @staticmethod
    def validate_height(
        height: int
    ) -> None:
        """
        Check that the 'height' provided is valid
        according to our settings, or raise an
        exception if invalid.
        """
        ParameterValidator.validate_mandatory_number_between('height', height, MINIMUM_DIMENSIONS[1], MAXIMUM_DIMENSIONS[1])

    @staticmethod
    def validate_fps(
        fps: float
    ) -> None:
        """
        Check that the 'fps' provided is valid
        according to our settings, or raise an
        exception if invalid.
        """
        ParameterValidator.validate_mandatory_number_between('fps', fps, MINIMUM_FPS, MAXIMUM_FPS)
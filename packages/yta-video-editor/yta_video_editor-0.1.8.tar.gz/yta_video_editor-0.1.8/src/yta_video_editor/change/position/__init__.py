from yta_video_editor.change.position.absolute import PositionAbsoluteChange
from yta_video_editor.change.position.offset import PositionOffsetChange
from yta_validation.parameter import ParameterValidator
from typing import Union


class PositionChange:
    """
    Class to handle a video position change by
    managing the PositionAbsoluteChange and all
    the different PositionOffsetChange provided.
    """

    def __init__(
        self,
        position_absolute: Union[PositionAbsoluteChange, None] = None,
        position_offsets: list[PositionOffsetChange] = []
    ):
        ParameterValidator.validate_subclass_of('position_absolute', position_absolute, PositionAbsoluteChange)
        ParameterValidator.validate_list_of_subclasses_of('position_offsets', position_offsets, PositionOffsetChange)

        self.position_absolute = position_absolute
        """
        The absolute position in which the video must
        be placed.
        """
        self.position_offsets = position_offsets
        """
        The relative offsets that must be added to the
        absolute position of the video.
        """

    def get_position(
        self,
        t: float
    ) -> tuple[int, int]:
        """
        Get the final position in which the video must
        be placed according to the absolute position
        and relative offsets provided.

        This position must be used to place the video.
        """
        x, y = (
            self.position_absolute.get_position(t)
            if self.position_absolute is not None else
            # TODO: Maybe '("center", "center")' (?)
            (0, 0)
        )

        for position_offset in self.position_offsets:
            dx, dy = position_offset.get_offset(t)
            x += dx
            y += dy

        return (x, y)
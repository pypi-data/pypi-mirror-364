from yta_video_moviepy.t import T, get_number_of_frames
from abc import ABC, abstractmethod


class PositionAbsoluteChange(ABC):
    """
    Class that represent a variation of the video
    position by absolute values. This position
    should be used directly to position the video.
    """

    @property
    @abstractmethod
    def positions(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of positions calculated for all the
        video frames.
        """
        pass

    @abstractmethod
    def get_position(
        self,
        t: float
    ) -> tuple[int, int]:
        """
        Get the absolute position for the provided 't'
        frame time moment. This position must replace
        the current video position.
        """
        pass

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class PositionAbsoluteFromAtoB(PositionAbsoluteChange):
    """
    Move the video from A to B.
    """

    @property
    def positions(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of positions calculated for all the
        video frames.
        """
        if not hasattr(self, '_positions'):
            # TODO: Calculate properly
            # This is just a shitty example to be able
            # to check the classes structure and
            # behaviour
            self._positions = [
                (0 + i * 2, 0 + i * 2)
                for i in range(get_number_of_frames(self.duration, self.fps))
            ]

        return self._positions

    def __init__(
        self,
        # TODO: Maybe 'number_of_frames' instead of
        # 'duration' (?)
        video_duration: float,
        video_fps: float,
        origin: tuple[int, int] = (100, 100),
        destination: tuple[int, int] = (200, 200),
    ):
        self.duration = video_duration
        """
        The duration of the video, to be able to
        calculate the values for the different frame
        time moments.
        """
        self.fps = video_fps
        """
        The frames per second of the video, to be 
        able to calculate the values for the different
        frame time moments.
        """
        # TODO: Validate positions
        self.origin = origin
        self.destination = destination

    def get_position(
        self,
        t: float
    ) -> tuple[int, int]:
        """
        Get the absolute position for the provided 't'
        frame time moment. This position must replace
        the current video position.
        """
        return self.positions[T.frame_time_to_frame_index(t, self.fps)]
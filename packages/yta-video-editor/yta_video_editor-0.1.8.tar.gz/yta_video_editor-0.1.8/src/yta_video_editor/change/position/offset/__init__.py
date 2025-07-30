from yta_video_moviepy.t import T, get_number_of_frames
from abc import ABC, abstractmethod


class PositionOffsetChange(ABC):
    """
    Class that represent a variation of the video
    position respect to the main (absolute)
    position the video has. This offset should
    be added to the absolute position.

    This is for the kind of effects that modify
    the relative position of the video. For 
    example, making the video bounce or move in
    circles. It is relative to its current 
    position and not about an absolute position
    in the scene.
    """

    @property
    @abstractmethod
    def offsets(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of offsets calculated for all the
        video frames.
        """
        pass

    @abstractmethod
    def get_offset(
        self,
        t: float
    ) -> tuple[int, int]:
        """
        Get the relative offset for the provided 't'
        frame time moment. This offset must be added
        to the current video position.
        """
        pass

# These classes below are custom made and
# must be in other module to avoid mixing
# the imports maybe
class PositionOffsetShake(PositionOffsetChange):
    """
    Shake the video in the current position.
    """

    @property
    def offsets(
        self
    ) -> list[tuple[int, int]]:
        """
        The list of offsets calculated for all the
        video frames.
        """
        if not hasattr(self, '_offsets'):
            # TODO: Calculate properly
            # This is just a shitty example to be able
            # to check the classes structure and
            # behaviour
            import math
            import random
            frequency = 25

            self._offsets = [
                (
                    math.sin(2 * math.pi * frequency * T.frame_index_to_frame_time(i, self.fps) + random.uniform(-0.5, 0.5)) * self.intensity * random.uniform(0.7, 1.0),
                    math.cos(2 * math.pi * frequency * T.frame_index_to_frame_time(i, self.fps) + random.uniform(-0.5, 0.5)) * self.intensity * random.uniform(0.7, 1.0)
                )
                for i in range(get_number_of_frames(self.duration, self.fps))
            ]

        return self._offsets

    def __init__(
        self,
        # TODO: Maybe 'number_of_frames' instead of
        # 'duration' (?)
        video_duration: float,
        video_fps: float,
        intensity: int = 4,
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
        # TODO: Validate intensity
        self.intensity = intensity
        """
        The intensity of the shake.

        TODO: Explain this better.
        """

    def get_offset(
        self,
        t: float
    ) -> tuple[int, int]:
        """
        Get the relative offset for the provided 't'
        frame time moment. This offset must be added
        to the current video position.
        """
        return self.offsets[T.frame_time_to_frame_index(t, self.fps)]
from yta_constants.video import VideoCombinatorAudioMode
from yta_video_moviepy.generator import MoviepyNormalClipGenerator
from yta_video_moviepy.t import T
from yta_video_base.combination import VideoAudioCombinator
from moviepy import VideoClip, CompositeVideoClip
from typing import Union


def _overlay_video(
    background_video: VideoClip,
    video: VideoClip,
    position: tuple = ('center', 'center'),
    audio_mode: VideoCombinatorAudioMode = VideoCombinatorAudioMode.BOTH_CLIPS_AUDIO
):
    """
    Overlay the provided 'video' on top of the also given
    'background_video'.
    """
    return CompositeVideoClip([
        background_video,
        video.with_position(position)
    ]).with_audio(VideoAudioCombinator(audio_mode).process_audio(background_video, video))

def put_video_over_black_background(
    video: VideoClip,
    position: tuple = ('center', 'center'),
    audio_mode: VideoCombinatorAudioMode = VideoCombinatorAudioMode.BOTH_CLIPS_AUDIO
) -> VideoClip:
    """
    Put the 'video' provided over a black background.

    We apply a black background to ensure the video size
    is the expected one and we dont have problems with
    movement.
    """
    black_background = MoviepyNormalClipGenerator.get_static_default_color_background(
        duration = video.duration,
        fps = video.fps
    )

    return _overlay_video(
        background_video = black_background,
        video = video,
        position = position,
        audio_mode = audio_mode
    )

def transform_video(
    video: VideoClip,
    factor: Union[int, list[int]],
    transform_fn: callable,
    apply_to: Union[any, None] = None,
    do_keep_duration: bool = True
) -> VideoClip:
    """
    Method to apply the 'video.transform' with the 
    parameters provided, using the 'transform_fn'
    given, that must have this structure:
    - `function(frame, factor)`

    The 'transform_fn' provided must return a numpy
    image that is the video frame modified.

    This method return the 'video' modified frame
    by frame.
    """
    def wrapped_transform(
        get_frame,
        t
    ):
        """
        This has the '(get_frame, t)' structure that
        the video transform function is expecting to
        be able to work with all the frames.
        """
        return transform_fn(get_frame(t), factor[T.frame_time_to_frame_index(t, video.fps)])

    return video.transform(
        func = wrapped_transform,
        apply_to = apply_to,
        keep_duration = do_keep_duration
    )
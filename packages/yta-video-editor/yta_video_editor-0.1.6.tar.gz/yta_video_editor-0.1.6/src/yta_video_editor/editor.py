"""
When we need to use videos generated with manim
we have many different types of videos, and we
need to ensure that the provided wrapper class
is one of the types the method we are using is
expecting.

If we are trying to overlaying a text which is
generated with a text manim wrapper class, we
need to raise an exception if the provided class
is not a text manim wrapper class, because the
process will fail as the video generated will be
different as the expected.

All the classes we have that belong to manim video
creation have the same structure, having a wrapper
class that internally uses a generator class to
actually build the video animation, so we need
those wrapper class names. But also, the wrapper
class name is the same as the file name but in
camel case and ending in 'Wrapper'.
"""
from yta_video_editor.modifications.video_modification import VideoModification
from yta_video_editor.settings import ROTATION_LIMIT, ZOOM_LIMIT, COLOR_HUE_CHANGE_LIMIT, COLOR_TEMPERATURE_CHANGE_LIMIT
from yta_video_base.parser import VideoParser
from yta_video_base.resize import resize_video
from yta_video_base.duration import set_video_duration, ExtendVideoMode
from yta_video_base.combination import VideoAudioCombinator
from yta_video_moviepy.generator import MoviepyNormalClipGenerator
from yta_video_moviepy.t import T
from yta_constants.manim import ManimAnimationType
from yta_constants.video import VideoCombinatorAudioMode, ExtendVideoMode
from yta_image_base.editor import ImageEditor
from yta_validation import PythonValidator
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator
from yta_file.handler import FileHandler
from yta_constants.file import FileSearchOption
from yta_programming.var import CaseStyleHandler
from yta_programming.path import DevPathHandler
from moviepy import CompositeVideoClip, VideoClip
from typing import Union


# TODO: Please, rename this class as this name is
# not a proper name
class VideoClassifier:

    # TODO: This method is no longer being used I think
    @staticmethod
    def get_manim_wrapper_class_names_from_files(
        abspath: str,
        files_to_ignore: list[str] = []
    ):
        """
        Obtain a list with the manim wrapper class names of
        all the available files that are in the provided
        'abspath', excluding the ones in the also given
        'files_to_ignore'. The file name is turned into the
        wrapper class name and returned.
        """
        files_to_ignore = (
            [files_to_ignore]
            if PythonValidator.is_string(files_to_ignore) else
            files_to_ignore
        )

        if not PythonValidator.is_list_of_string(files_to_ignore):
            raise Exception('The "files_to_ignore" parameter provided is not a valid list of strings.')

        # Transform the file name in the wrapper class that is inside
        transform_function = lambda file: CaseStyleHandler.snake_case_to_upper_camel_case(file.split("/")[-1].replace(".py", ""))

        return [
            f'{transform_function(file)}Wrapper'
            for file in FileHandler.list_items(abspath, FileSearchOption.FILES_ONLY, '*.py')
            if not any(file.endswith(file_to_ignore) for file_to_ignore in files_to_ignore)
        ]

        # TODO: Maybe try another way of getting all the classes
        # within a module, not a file, and identify like I tried
        # with this 'get_manim_wrapper_class_names_from_files'
        # method that is not working because files change when
        # imported as library
        return VideoClassifier.get_manim_wrapper_class_names_from_files(
            f'{DevPathHandler.get_project_abspath()()}/video/generation/manim/classes/text/',
            ['__init__.py']
        )

SIZE_FACTOR = 4



from yta_video_editor.settings import ZOOM_LIMIT, COLOR_TEMPERATURE_CHANGE_LIMIT, COLOR_HUE_CHANGE_LIMIT, BRIGHTNESS_LIMIT, CONTRAST_LIMIT, SHARPNESS_LIMIT, WHITE_BALANCE_LIMIT
from abc import ABC



class _UseTransformFactor(ABC):
    """
    Abstract class to represent the classes that
    will transform the video, frame by frame,
    using a factor that has to be validated.
    """

    def _validate_factor_type(
        self,
        factor: Union[int, list[int]]
    ):
        """
        Check if the 'factor' provided is a positive number or
        a list of positive numbers and raise an exception if
        not.
        """
        if (
            not NumberValidator.is_number(factor) and
            not PythonValidator.is_list_of_numbers(factor)
        ):
            raise Exception('The "factor" parameter provided is not a positive number nor a list of positive numbers.')
        
    def _validate_factor_value(
        self,
        number_of_frames: int,
        factor: Union[int, list[int]],
        limit: Union[tuple[int, int], None] = None
    ):
        """
        Check if the 'factor' value provided is valid
        according to the given 'limit' and the number
        of video frames.
        """
        if len(factor) != number_of_frames:
            raise Exception(f'The amount of "factor" elements ({str(len(factor))}) is not the same as the number of frames ({str(number_of_frames)}).')
        
        # TODO: Check that the 'limit' provided is valid (?)
        if limit is not None:
            for f in factor:
                ParameterValidator.validate_mandatory_number_between('factor', f, limit[0], limit[1])
                # ParameterValidator.validate_mandatory_number_between('factor', f, COLOR_TEMPERATURE_CHANGE_LIMIT[0], COLOR_TEMPERATURE_CHANGE_LIMIT[1])

    def validate_and_process_transform_factor(
        self,
        number_of_frames: int,
        factor: Union[int, list[int]],
        limit: Union[tuple[int, int], None] = None
    ) -> Union[int, list[int]]:
        """
        Validate the provided 'factor', raising an
        exception if invalid, and process it to 
        return an array of factor values with
        'number_of_frames' elements.
        """
        self._validate_factor_type(factor)
    
        factor = (
            [factor] * number_of_frames
            if not PythonValidator.is_list(factor) else
            factor
        )

        self._validate_factor_value(number_of_frames, factor, limit)

        return factor

class _Color(_UseTransformFactor):
    """
    Class to handle the color variations of a
    video when inside a VideoEditor instance.
    """

    def __init__(
        self,
        editor: 'VideoEditor'
    ):
        self.editor: VideoEditor = editor
        """
        The VideoEditor instance this _Color instance
        belongs to.
        """

    def temperature(
        self,
        factor: Union[int, list[int]] = 0
    ) -> 'VideoEditor':
        """
        Set the color temperature of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`
        """
        factor = self.validate_and_process_transform_factor(self.editor._video.n_frames, factor, COLOR_TEMPERATURE_CHANGE_LIMIT)

        def _transform_fn(frame, factor):
            return ImageEditor(frame).color.temperature(factor).image

        self.editor._video = transform_video(
            video = self.editor._video,
            factor = factor,
            transform_fn = _transform_fn,
        )
        
        return self.editor
    
    def hue(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color hue of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`
        """
        factor = self.validate_and_process_transform_factor(self.editor._video.n_frames, factor, COLOR_HUE_CHANGE_LIMIT)

        def _transform_fn(frame, factor):
            return ImageEditor(frame).color.hue(factor).image

        self.editor._video = transform_video(
            video = self.editor._video,
            factor = factor,
            transform_fn = _transform_fn,
        )
        
        return self.editor
    
    def brightness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color brightness of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        factor = self.validate_and_process_transform_factor(self.editor._video.n_frames, factor, BRIGHTNESS_LIMIT)

        def _transform_fn(frame, factor):
            return ImageEditor(frame).color.brightness(factor).image

        self.editor._video = transform_video(
            video = self.editor._video,
            factor = factor,
            transform_fn = _transform_fn,
        )
        
        return self.editor
    
    def contrast(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color contrast of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        factor = self.validate_and_process_transform_factor(self.editor._video.n_frames, factor, CONTRAST_LIMIT)

        def _transform_fn(frame, factor):
            return ImageEditor(frame).color.contrast(factor).image

        self.editor._video = transform_video(
            video = self.editor._video,
            factor = factor,
            transform_fn = _transform_fn,
        )
        
        return self.editor

    def sharpness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color sharpness of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        factor = self.validate_and_process_transform_factor(self.editor._video.n_frames, factor, SHARPNESS_LIMIT)

        def _transform_fn(frame, factor):
            return ImageEditor(frame).color.sharpness(factor).image

        self.editor._video = transform_video(
            video = self.editor._video,
            factor = factor,
            transform_fn = _transform_fn,
        )
        
        return self.editor

    def white_balance(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color white balance of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`
        """
        factor = self.validate_and_process_transform_factor(self.editor._video.n_frames, factor, WHITE_BALANCE_LIMIT)

        def _transform_fn(frame, factor):
            return ImageEditor(frame).color.white_balance(factor).image

        self.editor._video = transform_video(
            video = self.editor._video,
            factor = factor,
            transform_fn = _transform_fn,
        )
        
        return self.editor

# TODO: This single editor is used in the
# image library as a simple editor that is
# called from the image class instance...
# so maybe this should be very simple. It
# is also in the 'yta_image_base' library 
# and not in a different one
class VideoEditor:
    """
    Class to simplify and encapsulate all the
    functionality related to video edition.

    This VideoEditor works editing the video
    that has been providing when instantiating
    this class. All the changes you make will
    be chained.

    # TODO: I read that an interesting thing 
    is to store the operations you want to do
    in a list, and to perform all of them when
    needed. You can also revert the steps in
    that way. How can we do that? Also, if we
    want to apply zoom and then apply zoom
    again, that shouldn't be possible. We can
    add one zoom attribute that is the one we
    will apply, but not zoom x zoom.
    """

    @property
    def video(
        self
    ) -> VideoClip:
        """
        The moviepy video we are editing, with
        all the changes applied.
        """
        return self._video
    
    @property
    def copy(
        self
    ) -> VideoClip:
        """
        A copy of the video we are editing, with
        all the changes applied.
        """
        return self.video.copy()

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
        video: Union[str, VideoClip]
    ):
        self._original_video = VideoParser.to_moviepy(
            video,
            do_include_mask = True,
            # do_calculate_real_duration = True
        )
        """
        The original video as it was loaded with
        no changes on it.
        """
        self._video = self._original_video.copy()
        """
        The moviepy video we are editing, with
        all the changes applied.
        """
        self._color: _Color = _Color(self)

    def zoom(
        self,
        factor: int = 100
    ) -> 'VideoEditor':
        """
        Apply zoom on the video. A factor of 1 means x0.01 zoom,
        which is a zoom out. A factor of 200 means x2.00 zoom,
        which is a zoom in.
        """
        ParameterValidator.validate_mandatory_number_between('factor', factor, ZOOM_LIMIT[0], ZOOM_LIMIT[1])

        factor = int(factor)

        new_size = (
            factor / 100 * self.video.size[0],
            factor / 100 * self.video.size[1]
        )

        self._video = put_video_over_black_background(self.video.resized(new_size))

        return self
    
    def move(
        self,
        x_variation: int = 0,
        y_variation: int = 0
    ) -> 'VideoEditor':
        """
        Apply a movement in the video, which means that it
        will be not centered if 'x_variation' and/or
        'y_variation' are different from zero.

        TODO: I don't like the 'move' method name
        """
        # TODO: Any limit must be set in a general VideoEditor
        # settings file
        X_LIMIT = (-1920, 1920)
        Y_LIMIT = (-1080, 1080)

        ParameterValidator.validate_mandatory_number_between('x_variation', x_variation, X_LIMIT[0], X_LIMIT[1])
        ParameterValidator.validate_mandatory_number_between('y_variation', y_variation, Y_LIMIT[0], Y_LIMIT[1])

        x_variation = int(x_variation)
        y_variation = int(y_variation)

        self._video = put_video_over_black_background(self.video, position = (x_variation, y_variation))

        return self
    
    def rotate(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Apply a rotation in the video. A positive rotation
        will rotate it clockwise, and a negative one,
        anti-clockwise. A factor of 90 means rotating it 90
        degrees to the right (clockwise).
        """
        ParameterValidator.validate_mandatory_number_between('factor', factor, ROTATION_LIMIT[0], ROTATION_LIMIT[1])

        factor = int(factor % 360)

        self._video = put_video_over_black_background(self.video.rotated(factor))

        return self
    
    # TODO: Maybe these ones below could be with
    # the dynamic attribute format (single value,
    # array, etc.)
    def set_color_temperature(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color temperature of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`

        This is a shortcut of:
        - `VideoEditor(video).color.temperature(factor)`.
        """
        return self.color.temperature(factor)

    def set_color_hue(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color hue of the video.

        Limits of the 'factor' attribute:
        - `[-50, 50]`

        This is a shortcut of:
        - `VideoEditor(video).color.hue(factor)`.
        """
        return self.color.hue(factor)
    
    def set_color_brightness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color brightness of the image.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.brightness(factor)`.
        """
        return self.color.brightness(factor)

    def set_color_contrast(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color contrast of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.contrast(factor)`.
        """
        return self.color.contrast(factor)

    def set_color_sharpness(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color sharpness of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.sharpness(factor)`.
        """
        return self.color.sharpness(factor)

    def set_color_white_balance(
        self,
        factor: int = 0
    ) -> 'VideoEditor':
        """
        Set the color white_balance of the video.

        Limits of the 'factor' attribute:
        - `[-100, 100]`

        This is a shortcut of:
        - `VideoEditor(video).color.white_balance(factor)`.
        """
        return self.color.white_balance(factor)

    # def set_test(
    #     self,
    #     parameter: Union['MakeFrameParameterSingleValue', 'MakeFrameParameterValues', 'MakeFrameParameterProgression', 'MakeFrameParameterGraphic'],
    # ):
    #     ParameterValidator.validate_mandatory_instance_of('parameter', parameter, ['MakeFrameParameterSingleValue', 'MakeFrameParameterValues', 'MakeFrameParameterProgression', 'MakeFrameParameterGraphic'])

    #     values = parameter.get_values(self.video.n_frames)

    #     from yta_video_moviepy.t import T

    #     def get_value_from_t(
    #         t: float,
    #         fps: float
    #     ) -> float:
    #         """
    #         Obtain the value for the given 't' video time
    #         moment.
    #         """
    #         return values[T.frame_time_to_frame_index(t, self.video.fps)]
        
    #     # According to the effect or change we are
    #     # applying, modify the frame or video

    #     self.editor._video = self.editor._video.transform(
    #         lambda get_frame, t:
    #         ImageEditor(get_frame(t)).color.temperature(factor).image
    #     )
    #     # TODO: Do it
    #     pass
    
    def save_as(
        self,
        filename: str
    ) -> str:
        """
        Save the video with all the modifications to
        the provided 'filename'.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        self.video.write_videofile(filename)

        return filename


class VideoEditorOld:
    """
    Class to wrap the functionality related to
    editing one single video. This is not a
    project manager, is just the tools and 
    options we have to edit one single video.
    """

    _video: VideoClip = None

    @property
    def video(
        self
    ):
        return self._video

    def __init__(
        self,
        video: VideoClip
    ):
        self._video = VideoParser.to_moviepy(video, do_include_mask = True, do_calculate_real_duration = True)

    def overlay_text(
        self,
        text_generator_wrapping_instance: 'BaseManimAnimationWrapper'
    ):
        self._validate_is_manim_wrapper_instance_of_type(text_generator_wrapping_instance, ManimAnimationType.TEXT_ALPHA)
        
        video = VideoParser.to_moviepy(text_generator_wrapping_instance.generate(), do_include_mask = True)
        video = _prepare_video(self.video, video, 1)
        video = _overlay_video(self.video, video, position = ('center', 'center'), audio_mode = VideoCombinatorAudioMode.ONLY_MAIN_CLIP_AUDIO)

        return video
    
    def overlay_video_without_alpha_fullscreen(
        self,
        video: VideoClip,
        audio_mode: VideoCombinatorAudioMode = VideoCombinatorAudioMode.BOTH_CLIPS_AUDIO
    ):
        """
        Useful to show a stock video while the main clip is
        still speaking, or to focus on the stock video.
        """
        video = VideoParser.to_moviepy(video)
        audio_mode = VideoCombinatorAudioMode.to_enum(audio_mode)

        video = _prepare_video(self.video, video, 1)
        video = _overlay_video(self.video, video, position = ('center', 'center'), audio_mode = audio_mode)

        return video

    def overlay_video_without_alpha_non_fullscreen(
        self,
        video: VideoClip,
        audio_mode: VideoCombinatorAudioMode = VideoCombinatorAudioMode.BOTH_CLIPS_AUDIO
    ):
        """
        Useful to add a video like a reel or stock while the
        main clip is still visible.
        """
        video = VideoParser.to_moviepy(video)
        audio_mode = VideoCombinatorAudioMode.to_enum(audio_mode)

        video = _prepare_video(self.video, video, SIZE_FACTOR)
        video = _overlay_video(self.video, video, position = ('center', 'center'), audio_mode = audio_mode)

        return video
    
    def overlay_video_with_alpha_fullscreen(
        self,
        video: VideoClip,
        audio_mode: VideoCombinatorAudioMode = VideoCombinatorAudioMode.BOTH_CLIPS_AUDIO
    ):
        """
        Useful to add an alphascreen, a transition or
        another kind of videos.
        """
        video = VideoParser.to_moviepy(video, do_include_mask = True)
        audio_mode = VideoCombinatorAudioMode.to_enum(audio_mode)

        video = _prepare_video(self.video, video, 1)
        video = _overlay_video(self.video, video, position = ('center', 'center'), audio_mode = audio_mode)

        return video
    
    def overlay_video_with_alpha_non_fullscreen(
        self,
        video: VideoClip,
        audio_mode: VideoCombinatorAudioMode = VideoCombinatorAudioMode.BOTH_CLIPS_AUDIO
    ):
        """
        Useful for something that I don't know right now.

        TODO: Please, improve this doc... omg
        """
        video = VideoParser.to_moviepy(video, do_include_mask = True)
        audio_mode = VideoCombinatorAudioMode.to_enum(audio_mode)

        video = _prepare_video(self.video, video, SIZE_FACTOR)
        video = _overlay_video(self.video, video, position = ('center', 'center'), audio_mode = audio_mode)

        return video

    # Basic effects imitating capcut here below
    def zoom(
        self,
        factor: int = 100
    ):
        """
        Apply a zoom in the video. 1% means zooming out to 1/100 of
        the video size, while 500% means zooming in to 5 times its 
        size.

        TODO: The 'zoom' method name is not very self-descriptive
        """
        ParameterValidator.validate_mandatory_number_between('factor', factor, ZOOM_LIMIT[0], ZOOM_LIMIT[1])
        
        factor = int(factor)

        # We apply a black background to ensure the video size
        # is the expected one and no problems with resizing
        black_background = MoviepyNormalClipGenerator.get_static_default_color_background(
            duration = self.video.duration,
            fps = self.video.fps
        )

        new_size = (
            factor / 100 * self.video.size[0],
            factor / 100 * self.video.size[1]
        )

        return self._put_over_black_background(self.video.resized(new_size))
    
    def move(
        self,
        x_variation: int = 0,
        y_variation: int = 0
    ):
        """
        Apply a movement in the video, which means that it will be 
        not centered if 'x_variation' and/or 'y_variation' are 
        different from zero.

        TODO: I don't like the 'move' method name
        """
        # TODO: Any limit must be set in a general VideoEditor
        # settings file
        X_LIMIT = (-1920, 1920)
        Y_LIMIT = (-1080, 1080)

        ParameterValidator.validate_mandatory_number_between('x_variation', x_variation, X_LIMIT[0], X_LIMIT[1])
        ParameterValidator.validate_mandatory_number_between('y_variation', y_variation, Y_LIMIT[0], Y_LIMIT[1])

        x_variation = int(x_variation)
        y_variation = int(y_variation)
        
        return self._put_over_black_background(self.video, position = (x_variation, y_variation))
    
    def rotate(
        self,
        factor: int = 0
    ):
        ParameterValidator.validate_mandatory_number_between('factor', factor, ROTATION_LIMIT[0], ROTATION_LIMIT[1])

        factor = int(factor % 360)

        return self._put_over_black_background(self.video.rotated(factor))
        
    def change_color_temperature(
        self,
        factor: int = 0
    ):
        ParameterValidator.validate_mandatory_number_between('factor', factor, COLOR_TEMPERATURE_CHANGE_LIMIT[0], COLOR_TEMPERATURE_CHANGE_LIMIT[1])
        
        # TODO: Do I need to copy() (?)
        return self.video.transform(
            lambda get_frame, t:
            ImageEditor.modify_color_temperature(get_frame(t), factor)
        )
    
    def change_color_hue(
        self,
        factor: int = 0
    ):
        ParameterValidator.validate_mandatory_number_between('factor', factor, COLOR_HUE_CHANGE_LIMIT[0], COLOR_HUE_CHANGE_LIMIT[1])
        
        # TODO: Do I need to copy() (?)
        return self.video.transform(
            lambda get_frame, t:
            ImageEditor.modify_color_hue(get_frame(t), factor)
        )
    
    # Internal utils below
    def _put_over_black_background(
        self,
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
            duration = self.video.duration,
            fps = self.video.fps
        )

        return _overlay_video(
            background_video = black_background,
            video = video,
            position = position,
            audio_mode = audio_mode
        )
    
    # TODO: Move this method to another place maybe
    def _validate_is_manim_wrapper_instance_of_type(
        self,
        manim_wrapper_instance: 'BaseManimAnimationWrapper',
        type: ManimAnimationType
    ):
        """
        Validate that the provided 'manim_wrapper_instance'
        is actually an instance of that class and also of
        the given 'type'.
        """
        # The instance must be an instance of the specific
        # class that identifies it as a manim animation
        # generator wrapper.
        # This class contains the parameters needed (with
        # their values actually set) and the animation
        # generator class that must be called with those
        # parameters to generate the animation video.
        if (
            not PythonValidator.is_subclass(manim_wrapper_instance, 'BaseManimAnimationWrapper') or
            not PythonValidator.is_an_instance(manim_wrapper_instance)
        ):
            raise Exception('The "text_generator_wrapping_instance" is not a valid instance of a subclass of "BaseManimAnimationWrapper" class.')
        
        type = ManimAnimationType.to_enum(type)

        # Validate the wrapping instance is of the expected
        # type
        # TODO: Isn't this 'not in' (?)
        if type in manim_wrapper_instance.types:
            raise Exception('The provided "text_generator_wrapping_instance" is not an instance of a manim text generation class.')

    

def _prepare_video(
    main_video: VideoClip,
    video: VideoClip,
    size_factor: float = 1.0
):
    """
    Resize the 'video' according to the 'main_video' dimensions
    and enshort the 'video' if larger than the 'main_video'.
    """
    # We resize the 'video' to fit expected size
    video = resize_video(video, tuple(
        size_element / size_factor
        for size_element in main_video.size
    ))
    # We ensure the video is not larger than the main one
    video = set_video_duration(video, main_video.duration, extend_mode = ExtendVideoMode.DONT_ENLARGE)

    return video

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





# TODO: Move this to a better place
    
# TODO: I'm creating this raw class to use as a valid
# and working example of what I want to have in code
# and to apply, so later I can think about the best
# structure and hierarchy to allow it



class OverlayTextVideoModification(VideoModification):
    """
    Simple class that represents a video modification that
    consist of a text that shown over a video.
    """
    
    text: str = None
    start_time: float = None
    end_time: float = None
    generator_class: any = None

    def __init__(
        self,
        text: str,
        start_time: float
    ):
        # TODO: Add all parameters and validate them
        # TODO: This is an specific effect that will use a manim
        # wrapper class to build the text that will be overlayed
        # so I'm not sure how to handle this (inherit, accept the
        # wrapper class as parameter, etc.)
        pass

    def apply(
        self,
        video: VideoClip
    ) -> VideoClip:
        # TODO: Generate the text and apply it
        return video

"""
So, we have an 'OverlayTextVideoModification' which is an
specific modification that consist of adding a text in overlay
mode. This is a 'VideoModification', so it will be accepted
as a VideoModification valid class to apply. We can apply it.
"""



# 1. Videos must be 60fps both of them to simplify
# 2. The main video (background_video) must be 1920x1080 always,
#    and the other ones must be 1920x1080 or smaller
# 3. Duration of the video cannot be larger than the main video

# We should add a VideoModifications matrix in which we have
# layers that indicate the moment in which the modification has
# to be applied. Layer 1 will be prior, so once all layer 1
# modifications has been completed, layer 2 are applied. This
# is how editors work and also the better way to handle 
# priority. It is not the same applying a greenscreen and then
# an effect than applying the effect first to the clip and then
# the greenscreen that wraps the whole video.

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
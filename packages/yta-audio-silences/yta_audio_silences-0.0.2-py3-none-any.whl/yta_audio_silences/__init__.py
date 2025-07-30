"""
Welcome to Youtube Autonomous Audio Silences
Module.
"""
from yta_validation.parameter import ParameterValidator
from yta_programming.decorators.requires_dependency import requires_dependency
from typing import Union

import numpy as np


class AudioSilence:
    """
    Class to simplify and encapsulate the interaction with
    audio silences.
    """

    @staticmethod
    @requires_dependency('pydub', 'yta_audio_silences', 'pydub')
    def detect(
        audio: 'AudioSegment',
        min_silence_ms: int = 250
    ):
        """
        Detect the silences of a minimum of
        'min_silence_ms' milliseconds time and
        return an array containing tuples with
        the start and the end of the silence
        moments.

        This method returns an array of tuples
        with the start and the end of each
        silence expressed in seconds.

        This method needs the 'pydub' library.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, Union[str, 'BytesIO', 'ndarray', 'AudioNumpy', 'AudioClip', 'AudioSegment'])
        ParameterValidator.validate_mandatory_positive_int('min_silence_ms', min_silence_ms, do_include_zero = False)

        from pydub import silence
        
        # TODO: This below has been commented to avoid 
        # the import of the base library. It was also
        # attached to this parameter:
        # audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioNumpy', 'AudioClip', 'AudioSegment'],
        # audio = AudioParser.to_audiosegment(audio)

        dBFS = audio.dBFS
        # TODO: Why '- 16' (?) I don't know
        silences = silence.detect_silence(audio, min_silence_len = min_silence_ms, silence_thresh = dBFS - 16)

        # [(1.531, 1.946), (..., ...), ...] in seconds
        return [
            ((start / 1000), (stop / 1000))
            for start, stop in silences
        ]
    
    @staticmethod
    @requires_dependency('pydub', 'yta_audio_silences', 'pydub')
    def create(
        duration: float,
        sample_rate: Union[int, None] = None
    ) -> 'AudioSegment':
        """
        Create a silence audio as a pydub AudioSegment
        of the given 'duration' (in seconds) with the
        also given 'sample_rate'.

        This method needs the 'pydub' optional library.
        """
        ParameterValidator.validate_mandatory_positive_number('duration', duration, do_include_zero = False)
        ParameterValidator.validate_positive_int('sample_rate', sample_rate,  do_include_zero = False)

        from pydub import AudioSegment

        sample_rate = (
            44_100
            if sample_rate is None else
            sample_rate
        )
        
        return AudioSegment.silent(duration * 1000, sample_rate)
    
    @staticmethod
    def create_numpy(
        duration: float,
        channels: int,
        bytes_per_sample: int,
        sample_rate: Union[int, None] = None
    ) -> np.ndarray:
        """
        Create a numpy array that represents a silence
        audio with the provided parameters.

        This method only needs the 'numpy' library and
        not 'pydub'. You can convert this numpy array
        to an AudioSegment instance by doing this:

        ```
        audio = AudioSegment(
            data = create_numpy(...).tobytes(),
            sample_width = bytes_per_sample // 8,
            frame_rate = sample_rate,
            channels = channels
        )
        ```
        """
        ParameterValidator.validate_mandatory_positive_number('duration', duration, do_include_zero = False)
        ParameterValidator.validate_mandatory_number_between('channels', channels, 1, 2)
        ParameterValidator.validate_mandatory_positive_int('bytes_per_sample', bytes_per_sample, do_include_zero = False)
        ParameterValidator.validate_positive_number('sample_rate', sample_rate, do_include_zero = False)

        # 24 could be accepted but is special and
        # we ignore it by now
        if bytes_per_sample not in [8, 16, 32]:
            raise Exception('The "bytes_per_sample" parameter provided is not valid.')
        
        sample_rate = (
            44_100
            if sample_rate is None else
            sample_rate
        )

        number_of_samples = int(duration * sample_rate)

        dtype = {
            8: np.uint8, # 8-bit PCM uses [0,255], silence is 128
            16: np.int16, # 16-bit PCM uses [-32768,32767], silence is 0
            32: np.int32
        }[bytes_per_sample]

        silence_value = {
            np.uint8: 128,
            np.int16: 0,
            np.int32: 0
        }[dtype]

        return (
            np.full(number_of_samples, silence_value, dtype = dtype)
            if channels == 1 else
            np.full((number_of_samples, channels), silence_value, dtype = dtype)
        )
    
__all__ = [
    'AudioSilence'
]
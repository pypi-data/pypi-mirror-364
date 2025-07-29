from typing import Any, Generator, Literal

from gradio import Error
from kokoro import KPipeline
from loguru import logger
from numpy import dtype, float32, ndarray
from soundfile import write
from torch import zeros

from vocalizr import AUDIO_FILE_PATH, PIPELINE


@logger.catch
def save_file_wav(audio: ndarray[tuple[float32], dtype[float32]]) -> None:
    """
    Saves an audio array to a WAV file using the specified sampling rate. If the saving
    operation fails, it logs the exception and raises a RuntimeError.

    :param ndarray[tuple[float32],dtype[float32]] audio: The audio data to be saved.
        Must be a NumPy array of data type float32, representing the audio signal
        to be written to the file.

    :return: This function does not return a value.
    :rtype: None
    """
    try:
        logger.info(f"Saving audio to {AUDIO_FILE_PATH}")
        write(file=AUDIO_FILE_PATH, data=audio, samplerate=24000)
    except Exception as e:
        logger.exception(f"Failed to save audio to {AUDIO_FILE_PATH}: {e}")
        raise RuntimeError(f"Failed to save audio to {AUDIO_FILE_PATH}: {e}") from e


@logger.catch
def generate_audio_for_text(
    text: str,
    voice: str = "af_heart",
    speed: float = 1.0,
    save_file: bool = False,
    debug: bool = False,
    char_limit: int = -1,
) -> Generator[
    tuple[Literal[24000], ndarray[tuple[float32], dtype[float32]]]
    | tuple[int, ndarray],
    Any,
    None,
]:
    """
    Generates audio from the provided text using the specified voice and speed.
    It allows saving the generated audio to a file if required. The function
    yields tuples containing the audio sampling rate and the audio data as a
    NumPy array.

    :param str text: The input text to generate audio for. If CHAR_LIMIT is set to a
        positive value, the text will be truncated to fit that limit.

    :param str voice: The voice profile to use for audio generation.
        Defaults to "af_heart".

    :param float speed: The speed modifier for audio generation. Defaults to 1.0.

    :param bool save_file: Whether to save the generated audio to a file. Defaults
        to False.

    :param bool debug: Whether to enable debug mode. Defaults to False.

    :param int char_limit: The maximum number of characters to include in the input

    :return: A generator that yields tuples, where the first element is the
        fixed sampling rate of 24,000 Hz, and the second element is a NumPy
        array representing the generated audio data.
    :rtype: Generator[tuple[Literal[24000], NDArray[float32]], Any, None]
    """
    if not text:
        logger.exception("No text provided")
    elif len(text) < 4:
        logger.exception(f"Text too short: {text} with length {len(text)}")
    text = text if char_limit == -1 else text.strip()[:char_limit]
    generator: Generator[KPipeline.Result, None, None] = PIPELINE(
        text=text, voice=voice, speed=speed
    )
    first = True
    for _, _, audio in generator:
        if audio is None or isinstance(audio, str):
            logger.exception(f"Unexpected type (audio): {type(audio)}")
            raise Error(message=f"Unexpected type (audio): {type(audio)}")
        if debug:
            logger.info(f"Generating audio for '{text}'")
        audio_np: ndarray[tuple[float32], dtype[float32]] = audio.numpy()
        if save_file:
            if debug:
                logger.info(f"Saving audio file at {AUDIO_FILE_PATH}")
            save_file_wav(audio=audio_np)
        yield 24000, audio_np
        if first:
            first = False
            yield 24000, zeros(1).numpy()

"""Module aim to generate audio and the file result in M4B
"""
from typing import List, Callable, Dict, Any
import logging
import sys
import time
import os
import tempfile
import asyncio
import pyttsx3
import gtts
import edge_tts
import ffmpeg

LANGUAGE_DICT = {"it":"it"}
LANGUAGE_DICT_PYTTS = {"it":"italian", "en":"default"}
voice_edge = "" #pylint: disable=C0103

BIT_RATE_HUMAN = 40

engine_ptts = None #pylint: disable=C0103
loop = None #pylint: disable=C0103

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_back_end_tts() -> str:
    """Get the TTS engine for the system's operating system.
    
    Returns:
        The string name of the engine used for the caller's operating system.
    """
    os_engine_map = {
        "win32": "EDGE_TTS",
        "cygwin": "EDGE_TTS",
        "darwin": "GTTS"
    }
    return os_engine_map.get(sys.platform, "PYTTS")

async def get_voices_edge_tts(lang:str=LANGUAGE_DICT["it"]) -> List[Dict[str, Any]]:
    """get FEMALE voices in target language from EDGE-TTS.
    
    Arguments:
        lang: The desired language abbreviation.
    
    Returns:
        ret: A list of matching voice mappings based on lang.
    """
    try:
        vs = await edge_tts.VoicesManager.create()
        ret = vs.find(Gender="Female", Language=lang)
    except Exception: #TODO add a best exception handling #pylint: disable=W0511,W0718
        ret = []
    return ret
async def generate_audio_edge_tts(text_in:str,
                                  out_mp3_path:str, *,
                                  lang:str="it", # pylint: disable=W0613
                                  voice:str) -> bool:
    """Generate audio with EDGE-TTS starting from text_in string
    and save it in out_mp3_path path.
    
    Arguments:
        text_in: The text used to generate the TTS.
        out_mp3_path: The path to save the result MP3 file.
        lang: The desired language abbreviation.
        voice: The TTS engine voice ID.

    Returns:
        True if the function succesfully saves the MP3 file.
    """
    com = edge_tts.Communicate(text_in, voice)
    await com.save(out_mp3_path)
    return True

def __split_text_into_chunks(string:str, max_chars:int=gtts.gTTS.GOOGLE_TTS_MAX_CHARS):
    result = []
    temp = string
    while len(temp)>max_chars:
        # Find the last space within the maximum character limit
        last_space = temp.rfind(' ', 0, max_chars)
        if last_space != -1:
            # If a space is found, cut the string at that point
            result.append(temp[:last_space])
        else:
            # If no space is found within the limit, just cut at max_chars
            break
        temp = temp[last_space+1:]
    result.append(temp)
    return result

def __save_tts_audio_gtts(text_to_speech_str:str, mp3_path:str, lang:str) -> bool:
    re_try = True
    while re_try:
        try:
            tts = gtts.gTTS(text_to_speech_str, lang=LANGUAGE_DICT[lang],
                            slow=False, tld="com")
            tts.save(mp3_path)
            time.sleep(1)
            re_try = False
        except gtts.gTTSError as ex:
            re_try = False
            time.sleep(1)
            logger.error("gtts error: %s", ex.msg)
            return False
    return True

def generate_audio_gtts(text_in:str, out_mp3_path:str, *, lang:str="it") -> bool:
    """Generate audio using GTTS apis.
    
    Arguments:
        text_in: The text used to generate the TTS.
        out_mp3_path: The path to save the result MP3 file.
        lang: The desired language abbreviation.

    Returns:
        True if the function succesfully saves the MP3 file.
    """
    chunks = __split_text_into_chunks(text_in)
    if len(chunks)>1:
        __sub_audio(__save_tts_audio_gtts, out_mp3_path, chunks, lang)
    else:
        return __save_tts_audio_gtts(text_in, out_mp3_path, lang)
    return True

def generate_audio_pytts(text_in:str, out_mp3_path:str, *, lang:str="it") -> bool:
    """Generate audio using PYTTS apis.
    
    Arguments:
        text_in: The text used to generate the TTS.
        out_mp3_path: The path to save the result MP3 file.
        lang: The desired language abbreviation.

    Returns:
        True if the function succesfully saves the MP3 file.
    """
    if engine_ptts.getProperty("voice") != lang:
        engine_ptts.setProperty("voice", LANGUAGE_DICT_PYTTS[lang])
    engine_ptts.save_to_file(text_in, out_mp3_path)
    engine_ptts.runAndWait()
    return True

def __sub_audio(audio_generator:Callable[[str, str], bool],
              output_path_mp3:str, chunks_sub_text:str, lang:str):
    dummy_mp3 = []
    with tempfile.TemporaryDirectory() as dummy_temp_folder:
        for idx, chunk in enumerate(chunks_sub_text, start=1):
            dummy_mp3_path = os.path.join(dummy_temp_folder, f"dummy{idx}.mp3")
            if audio_generator(chunk, dummy_mp3_path, lang):
                dummy_mp3.append(ffmpeg.input(dummy_mp3_path))
        if len(dummy_mp3)>0:
            dummy_concat = ffmpeg.concat(*dummy_mp3, v=0, a=1)
            out = ffmpeg.output(dummy_concat, output_path_mp3, f='mp3')
            out.run()

def generate_m4b(output_path: str, chapter_paths: List[str], ffmetadata: str) -> None:
    """Generate the final audiobook starting from MP3s and METADATAs.
    
    Arguments:
        output_path: The path to save the final audiobook.
        chapter_paths: The paths where each chapter was saved.
        ffmetadata: The ffmetadata file content.
    """
    inputs_mp3 = [ffmpeg.input(cp) for cp in chapter_paths]
    joined = ffmpeg.concat(*inputs_mp3, v=0, a=1)
    # Build FFmpeg command for setting metadata
    out = ffmpeg.output(joined, output_path, f='mp4', map_metadata=0, audio_bitrate=BIT_RATE_HUMAN)
    ffmetadata_path = "ffmetada"
    with open(ffmetadata_path, "w", encoding="UTF-8") as file_ffmetadata:
        file_ffmetadata.write(ffmetadata)
    out = out.global_args('-f', 'ffmetadata', '-i', ffmetadata_path)
    try:
        ffmpeg.run(out)
    except ffmpeg.Error as e:
        logger.error(e.stderr.decode())
        raise e

def init(backend:str) -> None:
    """Init back end code per text-to-speech
    SUPPORTED: EDGE_TTS, PYTTS, GTTS.
    
    Arguments:
        backend: The string name of the TTS engine.
    """
    global engine_ptts #pylint: disable=W0603
    global voice_edge  #pylint: disable=W0603
    global loop        #pylint: disable=W0603
    if backend == "PYTTS":
        engine_ptts = pyttsx3.init()
        engine_ptts.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
    elif backend == "EDGE_TTS":
        asyncio.set_event_loop(asyncio.ProactorEventLoop())
        loop = asyncio.get_event_loop_policy().get_event_loop()
        voices = loop.run_until_complete(get_voices_edge_tts(lang="it"))
        voice_edge = voices[0]["Name"]

def generate_audio(text_in:str, out_mp3_path:str, *,
                   lang:str="it", backend:str="PYTTS") -> bool:
    """Generating audio using tts apis.
    Arguments:
        text_in: The text used to generate the TTS.
        out_mp3_path: The path to save the result MP3 file.
        lang: The desired language abbreviation.
        backend: The string name of the TTS engine.
    Returns:
        True if the function succesfully saves the MP3 file.
    """
    ret_val = True
    text_in = text_in.strip()
    if len(text_in) == 0:
        return False
    if backend == "GTTS":
        ret_val = generate_audio_gtts(text_in, out_mp3_path, lang=lang)
    elif backend == "PYTTS":
        ret_val = generate_audio_pytts(text_in, out_mp3_path, lang=lang)
    elif backend == "EDGE_TTS":
        loop_audio = asyncio.get_event_loop_policy().get_event_loop()
        loop_audio.run_until_complete(generate_audio_edge_tts(text_in, out_mp3_path,
                                                              lang=lang, voice=voice_edge))
    return ret_val

def close_edge_tts() -> None:
    """Need to close the async io process."""
    global loop #pylint: disable=W0603,W0602
    if loop:
        loop.close()

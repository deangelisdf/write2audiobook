from typing import List, Callable, Tuple
import logging
import os
import tempfile
import ffmpeg

BIT_RATE_HUMAN = 40

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sub_audio(audio_generator:Callable[[str, str], bool],output_path_mp3:str, chunks_sub_text:str):
    dummy_mp3 = []
    with tempfile.TemporaryDirectory() as dummy_temp_folder:
        for idx, chunk in enumerate(chunks_sub_text, start=1):
            dummy_mp3_path = os.path.join(dummy_temp_folder, f"dummy{idx}.mp3")
            if audio_generator(chunk, dummy_mp3_path):
                dummy_mp3.append(ffmpeg.input(dummy_mp3_path))
        if len(dummy_mp3)>0:
            dummy_concat = ffmpeg.concat(*dummy_mp3, v=0, a=1)
            out = ffmpeg.output(dummy_concat, output_path_mp3, f='mp3')
            out.run()

def generate_m4b(output_path: str, chapter_paths: List[str], ffmetadata_path: str):
    """Generate the final audiobook starting from MP3s and METADATAs"""
    inputs_mp3 = [ffmpeg.input(cp) for cp in chapter_paths]
    joined = ffmpeg.concat(*inputs_mp3, v=0, a=1)
    # Build FFmpeg command for setting metadata
    out = ffmpeg.output(joined, output_path, f='mp4', map_metadata=0, audio_bitrate=BIT_RATE_HUMAN)
    out = out.global_args('-f', 'ffmetadata', '-i', ffmetadata_path)
    try:
        ffmpeg.run(out)
    except ffmpeg.Error as e:
        logger.error(e.stderr.decode())
        raise e

#!/usr/bin/python3
"""
file: txt2audio.py
description: Convert your txt (UTF-8) to audiobook in M4B format
Usage example:
    python txt2audio.py document.txt
"""
import sys
import os
import logging
import asyncio
from backend_audio import m4b
from frontend import input_tool

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

if sys.platform in ("win32", "cygwin"):
    BACK_END_TTS = "EDGE_TTS"
elif sys.platform == "darwin":
    BACK_END_TTS = '"GTTS'
else:
    BACK_END_TTS = "PYTTS"
LANGUAGE = "it"

def main():
    """main function"""
    _, output_file_path = input_tool.get_sys_input(os.path.dirname(__file__),
                                                   format_output="mp3")
    text:str = ""
    with open(sys.argv[1], "r", encoding="UTF-8") as file:
        text = ''.join(file.readlines())

    m4b.init(BACK_END_TTS)
    if BACK_END_TTS == "PYTTS":
        m4b.generate_audio_pytts(text, output_file_path, lang=LANGUAGE)
    else:
        loop = asyncio.get_event_loop_policy().get_event_loop()
        try:
            voices = loop.run_until_complete(m4b.get_voices_edge_tts(lang=LANGUAGE))
            voice = voices[0]["Name"]
            loop.run_until_complete(m4b.generate_audio_edge_tts(text, output_file_path,
                                                                lang="it-IT", voice=voice))
        finally:
            loop.close()
    #metadata_output = ffmetadata_generator.generate_ffmetadata(audio_paths)
    #generate_m4b(output_file_path, chapters, metada_output, chapter_metadata=ch_metadatas)


if __name__ == "__main__":
    main()

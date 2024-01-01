#!/usr/bin/python3
import sys
import time
import zipfile
import tempfile
import os
import logging
import codecs
from typing import Dict, List, Tuple
from lxml   import etree
import pyttsx3
import gtts
import ffmpeg

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

BACK_END_TTS = "PYTTS"
LANGUAGE_DICT = {"it-IT":"it"}
LANGUAGE_DICT_PYTTS = {"it-IT":"italian", "en":"english"}

def generate_audio_pytts(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    if engine_ptts.getProperty("voice") != lang:
        voices = engine_ptts.getProperty('voices')
        engine_ptts.setProperty("voice", voices[0].id)
    engine_ptts.save_to_file(text_in, out_mp3_path)
    engine_ptts.runAndWait()
    return True

if __name__ == "__main__":
    sys.argv.append("Children Visiting Mothers in Prison_ITA.txt")
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input.epub>")
        exit(1)
    input_file_path=sys.argv[1]
    output_file_path=os.path.join(os.path.dirname(__file__), os.path.basename(input_file_path)[:-4]) + ".mp3"
    chapters = []
    metada_output = {}
    ch_metadatas = []

    if BACK_END_TTS == "PYTTS":
        engine_ptts = pyttsx3.init()
        #engine_ptts.setProperty('rate', 200)     # setting up new voice rate
        engine_ptts.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
    text=""
    with open(sys.argv[1], "r", encoding="UTF-8") as file:
        text = ''.join(file.readlines())
    generate_audio_pytts(text, output_file_path, lang="en")
    #generate_m4b(output_file_path, chapters, metada_output, chapter_metadata=ch_metadatas)

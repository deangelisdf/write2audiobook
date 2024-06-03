#!/usr/bin/python3
import sys
import os
import logging
import pyttsx3
import pptx
from pptx import presentation, slide
import edge_tts
import asyncio


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

BACK_END_TTS = "EDGE_TTS"
LANGUAGE_DICT = {"it-IT":"it"}
LANGUAGE_DICT_PYTTS = {"it-IT":"italian", "en":"english"}

async def get_voices_edge_tts(lang=LANGUAGE_DICT["it-IT"]):
    vs = await edge_tts.VoicesManager.create()
    return vs.find(Gender="Female", Language=lang)
async def generate_audio_edge_tts(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    com = edge_tts.Communicate(text_in, VOICE)
    await com.save(out_mp3_path)
    return True
def generate_audio_pytts(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    if engine_ptts.getProperty("voice") != lang:
        voices_property = engine_ptts.getProperty('voices')
        engine_ptts.setProperty("voice", voices_property[0].id)
    engine_ptts.save_to_file(text_in, out_mp3_path)
    engine_ptts.runAndWait()
    return True

def generate_audio_pytts(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    if engine_ptts.getProperty("voice") != lang:
        voices = engine_ptts.getProperty('voices')
        engine_ptts.setProperty("voice", voices[0].id)
    engine_ptts.save_to_file(text_in, out_mp3_path)
    engine_ptts.runAndWait()
    return True

def __get_notes(note: slide.NotesSlide) -> str:
    print(note)
    return ""
def __extract_text_from_slide(slide: slide.Slide) -> str:
        text_slide, text_note = "", ""
        if slide.has_notes_slide:
            text_note = __get_notes(slide.notes_slide)
        for shape in slide.shapes:
            if shape.has_text_frame:
                text_slide += shape.text
        text_slide = text_slide.strip()
        if len(text_note) != 0:
            text_slide += f"\n\nNote:\n{text_note}"
        return text_slide

def extract_pptx_text(path_pptx:str) -> str:
    text_out:str = ""
    p: presentation.Presentation = pptx.Presentation(path_pptx)
    for idx,s in enumerate(p.slides):
        text_out += f"\n\nSlide numero: {idx}\n"
        ts = __extract_text_from_slide(s)
        text_out += ts
        if len(ts) == 0:
            text_out += ""
    return text_out

if __name__ == "__main__":
    sys.argv.append("Convegno Napoli.pptx")
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input.pptx>")
        exit(1)
    input_file_path=sys.argv[1]
    output_file_path=os.path.join(os.path.dirname(__file__), os.path.basename(input_file_path)[:-5]) + ".mp3"
    chapters = []
    metada_output = {}
    ch_metadatas = []

    if BACK_END_TTS == "PYTTS":
        engine_ptts = pyttsx3.init()
        #engine_ptts.setProperty('rate', 200)     # setting up new voice rate
        engine_ptts.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
    text=extract_pptx_text(input_file_path)
    if BACK_END_TTS == "PYTTS":
        generate_audio_pytts(text, output_file_path, lang="en")
    else:
        loop = asyncio.get_event_loop_policy().get_event_loop()
        try:
            voices = loop.run_until_complete(get_voices_edge_tts(lang="it"))
            VOICE = voices[0]["Name"]
            loop.run_until_complete(generate_audio_edge_tts(text, output_file_path, lang="it-IT"))
        finally:
            loop.close()
    #generate_m4b(output_file_path, chapters, metada_output, chapter_metadata=ch_metadatas)

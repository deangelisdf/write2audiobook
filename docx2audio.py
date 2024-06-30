#!/usr/bin/python3
import sys
import time
import os
import logging
import asyncio
from typing import Dict, List, Tuple, Union
import pyttsx3
import gtts
import edge_tts
from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table, _Row
from docx.text.paragraph import Paragraph
from backend_audio import ffmetadata_generator
from backend_audio import m4b

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACK_END_TTS = "EDGE_TTS"
LANGUAGE_DICT = {"it-IT":"it"}
LANGUAGE_DICT_PYTTS = {"it-IT":"italian"}
VOICE = ""

TITLE_KEYWORD  = {"it-IT":"TITOLO",   "en":"TITLE"}
CHAPTER_KEYWORD= {"it-IT":"CAPITOLO", "en":"CHAPTER"}

def iter_block_items(parent:Union[Document, _Cell, _Row]):
    """
    Generate a reference to each paragraph and table child within *parent*,
    in document order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    elif isinstance(parent, _Row):
        parent_elm = parent._tr
    else:
        raise ValueError("something's not right")
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

async def get_voices_edge_tts(lang=LANGUAGE_DICT["it-IT"]):
    try:
        vs = await edge_tts.VoicesManager.create()
        ret = vs.find(Gender="Female", Language=lang)
    except Exception: #TODO add a best exception handling
        ret = []
    return ret
async def generate_audio_edge_tts(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    com = edge_tts.Communicate(text_in, VOICE)
    await com.save(out_mp3_path)
    return True

def __split_text_into_chunks(string:str, max_chars=gtts.gTTS.GOOGLE_TTS_MAX_CHARS):
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

def __save_tts_audio_gtts(text_to_speech_str:str, mp3_path:str) -> bool:
    re_try = True
    while re_try:
        try:
            tts = gtts.gTTS(text_to_speech_str, lang=LANGUAGE_DICT[lang], slow=False, tld="com")
            tts.save(mp3_path)
            time.sleep(1)
            re_try = False
        except gtts.gTTSError as ex:
            re_try = False #TODO set a proxy in case of error to retry with another IP
            time.sleep(1)
            logger.error(f"gtts error: {ex.msg}")
            return False
    return True

def generate_audio_gtts(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    chunks = __split_text_into_chunks(text_in)
    if len(chunks)>1:
        m4b.sub_audio(__save_tts_audio_gtts, out_mp3_path, chunks)
    else:
        return __save_tts_audio_gtts(text_in, out_mp3_path)
    return True

def generate_audio_pytts(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    if engine_ptts.getProperty("voice") != lang:
        engine_ptts.setProperty("voice", LANGUAGE_DICT_PYTTS[lang])
    engine_ptts.save_to_file(text_in, out_mp3_path)
    engine_ptts.runAndWait()
    return True

def generate_audio(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    """Generating audio using tts apis"""
    ret_val = True
    text_in = text_in.strip()
    if len(text_in) == 0:
        return False
    if BACK_END_TTS == "GTTS":
        ret_val = generate_audio_gtts(text_in, out_mp3_path, lang=lang)
    elif BACK_END_TTS == "PYTTS":
        ret_val = generate_audio_pytts(text_in, out_mp3_path, lang=lang)
    elif BACK_END_TTS == "EDGE_TTS":
        loop_audio = asyncio.get_event_loop_policy().get_event_loop()
        #try:
        loop_audio.run_until_complete(generate_audio_edge_tts(text_in, out_mp3_path, lang="it-IT"))
        #finally:
        #    loop_audio.close()
    return ret_val

def extract_chapters(doc:Document, 
                     style_start_chapter_name:List[str] = ['Heading 1', 'Title', 'Titolo']) -> List[Paragraph]:
    chapters: List[List[Paragraph]] = []
    temp:List[Paragraph] = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            if block.style.name in style_start_chapter_name:
                if len(temp) > 1:
                    chapters.append(temp)
                temp = []
            if len(block.text) == 0:
                continue
        temp.append(block)
    return [i for i in chapters if len(i)>0]

def get_text_from_chapter(chapter:List[Union[Paragraph, Table]], 
                          language="it-IT") -> Tuple[str, str]:
    title = chapter[0].text
    text = f"{TITLE_KEYWORD[language]}: {title}.\n"
    idx_list = 0
    for block in chapter[1:]:
        if isinstance(block, Paragraph):
            if block.style.name == 'List Paragraph':
                text += f"\t{idx_list}: {block.text}.\n"
                idx_list += 1
                continue
            idx_list = 0
            if block.style.name == 'Heading 2':
                text += f"\n.\n{CHAPTER_KEYWORD[language]}: "
            text += f"{block.text}\n"
        elif isinstance(block, Table):
            for row in block.rows:
                row_data = []
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        row_data.append(paragraph.text)
                text += "{}\n".format('\t'.join(row_data))
    return text, title

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error(f"Usage: {sys.argv[0]} <input.docx>")
        exit(1)
    input_file_path=sys.argv[1]
    output_file_path=os.path.join(os.path.dirname(__file__), os.path.basename(input_file_path)[:-len(".docx")]) + ".m4b"
    chapters = []
    chapters_path: List[str] = []
    title_list:List[str] = []
    metadata_book_output = {}
    ch_metadatas = []

    if BACK_END_TTS == "PYTTS":
        engine_ptts = pyttsx3.init()
        engine_ptts.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
    elif BACK_END_TTS == "EDGE_TTS":
        asyncio.set_event_loop(asyncio.ProactorEventLoop())
        loop = asyncio.get_event_loop_policy().get_event_loop()
        #try:
        voices = loop.run_until_complete(get_voices_edge_tts(lang="it"))
        VOICE = voices[0]["Name"]
        #finally:
        #    loop.close()
    doc = Document(input_file_path)
    chapters = extract_chapters(doc)
    for idref, chapter in enumerate(chapters):
        output_debug_path = f"{input_file_path}.c{idref}.txt"
        output_mp3_path   = f"{input_file_path}.c{idref}.mp3"
        text_chapther, title = get_text_from_chapter(chapter)
        title_list.append(title)
        logger.info(f"idref {idref}")
        with open(output_debug_path, "w", encoding="UTF-16") as out_debug_file:
            out_debug_file.write(text_chapther)
        if generate_audio(text_chapther, output_mp3_path):
            chapters_path.append(output_mp3_path)
    metadata_output = ffmetadata_generator.generate_ffmetadata(chapters_path, chapter_titles=title_list)
    with open("ffmetada", "w", encoding="UTF-8") as file_ffmetadata:
        file_ffmetadata.write(metadata_output)
    m4b.generate_m4b(output_file_path, chapters_path, "ffmetada")
    loop.close()

__author__ = "de angelis domenico francesco"
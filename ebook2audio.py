#!/usr/bin/python3
import sys
import time
import zipfile
import tempfile
import os
import logging
import codecs
import asyncio
from typing import Dict, Tuple
from lxml   import etree
import pyttsx3
import gtts
import edge_tts
from backend_audio import m4b
from backend_audio import ffmetadata_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACK_END_TTS = "EDGE_TTS"
LANGUAGE_DICT = {"it-IT":"it"}
LANGUAGE_DICT_PYTTS = {"it-IT":"italian"}
VOICE = ""

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

def extract_by_epub(epub_path:str, directory_to_extract_path:str) -> None:
    """Unzip the epub file and extract all in a temp directory"""
    logger.debug("Extracting input to temp directory %s." % directory_to_extract_path)
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_path)

def get_guide_epub(root_tree:etree.ElementBase) -> Dict[str,str]:
    """Get information about the guide information, described in content.opf file"""
    guide_res = {}
    for reference in root_tree.xpath("//*[local-name()='package']"
                                "/*[local-name()='guide']"
                                "/*[local-name()='reference']"):
        guide_res[reference.attrib['type']] = reference.attrib['href']
    return guide_res

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
def prepocess_text(text_in:str) -> str:
    """Remove possible character not audiable"""
    text_out = codecs.decode(bytes(text_in, encoding="utf-8"), encoding="utf-8")
    text_out = text_out.replace('\xa0', '')
    text_out = text_out.replace('\r\n\t', '')
    text_out = text_out.replace('\r\n', '\n')
    return text_out.strip()

def get_text_from_chapter(root_tree:etree._ElementTree,
                          idref_ch:str, content_dir_path:str,
                          guide_manifest:Dict[str,str]) -> Tuple[str, Dict[str,str]]:
    """Starting from content.opf xml tree, extract chapter html path
       and parse it to achieve the chapter"""
    text_result = ""
    for href in root_tree.xpath( f"//*[local-name()='package']"
                            f"/*[local-name()='manifest']"
                            f"/*[local-name()='item'][@id='{idref_ch}']"
                            f"/@href"):
        if href in guide_manifest.values():
            #Skip the chapter used as guide
            logging.debug(f"skipping {href}")
            continue
        xhtml_file_path = os.path.join(content_dir_path, href)
        subtree = etree.parse(xhtml_file_path, etree.HTMLParser())
        for ptag in subtree.xpath("//html/body/*"):
            for text in ptag.itertext():
                text_result += text
            text_result += "\n"
    return text_result, {}

def get_metadata(root_tree:etree._ElementTree) -> Dict[str,str]:
    """Extract basic metadata, as title, author and copyrights infos from content.opf"""
    metadata_leaf = root_tree.xpath("//*[local-name()='package']/*[local-name()='metadata']")[0]
    metadata_result = {}
    namespace = metadata_leaf.nsmap
    if None in namespace.keys():
        del namespace[None]
    title  = metadata_leaf.xpath("//dc:title", namespaces=namespace)
    if len(title)>0:
        metadata_result["title"] = title[0].text
    author = metadata_leaf.xpath("//dc:creator", namespaces=namespace)
    if len(author)>0:
        metadata_result["author"] = author[0].text
    rights = metadata_leaf.xpath("//dc:rights", namespaces=namespace)
    if len(rights)>0:
        metadata_result["copyright"] = rights[0].text
    return metadata_result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error(f"Usage: {sys.argv[0]} <input.epub>")
        exit(1)
    input_file_path=sys.argv[1]
    output_file_path=os.path.join(os.path.dirname(__file__), os.path.basename(input_file_path)[:-len(".epub")]) + ".m4b"
    chapters = []
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
    with tempfile.TemporaryDirectory() as tmp_dir:
        extract_by_epub(input_file_path, tmp_dir)
        logger.info(f"Parsing 'container.xml' file.")
        containerFilePath=os.path.join(tmp_dir, "META-INF/container.xml")
        tree = etree.parse(containerFilePath)
        for root_file_path in tree.xpath( "//*[local-name()='container']"
                                        "/*[local-name()='rootfiles']"
                                        "/*[local-name()='rootfile']"
                                        "/@full-path"):
            logger.info(f"Parsing '{root_file_path}' file.")
            content_file_path = os.path.join(tmp_dir, root_file_path)
            content_file_dir_path = os.path.dirname(content_file_path)
            tree = etree.parse(content_file_path)
            guide = get_guide_epub(tree)
            metadata_book_output = get_metadata(tree)
            logger.info(f"Parsed '{root_file_path}' file.")
            for idref in tree.xpath("//*[local-name()='package']"
                                    "/*[local-name()='spine']"
                                    "/*[local-name()='itemref']"
                                    "/@idref"):
                output_debug_path= os.path.join(os.path.dirname(output_file_path), f"{idref}.log")
                output_mp3_path  = os.path.join(os.path.dirname(output_file_path), f"{idref}.mp3")
                #TODO get chapter title by toc.nx
                text_chapther, metadata_ch = get_text_from_chapter(tree, idref, content_file_dir_path, guide)
                logger.info(f"idref {idref}")
                text_chapther = prepocess_text(text_chapther)
                with open(output_debug_path, "w", encoding="UTF-16") as out_debug_file:
                    out_debug_file.write(text_chapther)
                if generate_audio(text_chapther, output_mp3_path):
                    chapters.append(output_mp3_path)
    loop.close()
    metadata_output = ffmetadata_generator.generate_ffmetadata(chapters)
    with open("ffmetada", "w", encoding="UTF-8") as file_ffmetadata:
        file_ffmetadata.write(metadata_output)
    m4b.generate_m4b(output_file_path, chapters, "ffmetada")

__author__ = "de angelis domenico francesco"
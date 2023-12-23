#!/usr/bin/python3
import sys
import time
import zipfile
import tempfile
import os
import logging
import codecs
from typing import Dict, List
from lxml   import etree
import gtts
import ffmpeg

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

LANGUAGE_DICT = {"it-IT":"it"}

def extract_by_epub(epub_path:str, directory_to_extract_path:str) -> None:
    logger.debug("Extracting input to temp directory %s." % directory_to_extract_path)
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_path)

def get_guide_epub(root_tree:etree.ElementBase) -> Dict[str,str]:
    guide_res = {}
    for reference in root_tree.xpath("//*[local-name()='package']"
                                "/*[local-name()='guide']"
                                "/*[local-name()='reference']"):
        guide_res[reference.attrib['type']] = reference.attrib['href']
    return guide_res

def generate_audio(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    if len(text_in.strip()) == 0:
        return False
    try:
        tts = gtts.gTTS(text_in, lang=LANGUAGE_DICT[lang], slow=False, tld="com")
        tts.save(out_mp3_path)
    except gtts.gTTSError as ex:
        time.sleep(10)
        logger.error(f"gtts error: {ex.msg}")
        return False
    time.sleep(10)
    return True
def prepocess_text(text_in:str) -> str:
    text_out = codecs.decode(bytes(text_in, encoding="utf-8"), encoding="utf-8")
    text_out = text_out.replace('\xa0', '')
    return text_out

def get_text_from_chapter(root_tree:etree.ElementBase, idref:str, content_dir_path:str, guide_manifest:Dict[str,str]):
    text_chapther = ""
    metadata = {"chapter":""}
    for href in root_tree.xpath( f"//*[local-name()='package']"
                            f"/*[local-name()='manifest']"
                            f"/*[local-name()='item'][@id='{idref}']"
                            f"/@href"):
        if href in guide_manifest.values():
            logging.debug(f"skipping {href}")
            continue
        xhtmlFilePath = os.path.join(content_dir_path, href)
        subtree = etree.parse(xhtmlFilePath, etree.HTMLParser())
        title = subtree.xpath("//html/head/title")
        if len(title)>0:
            metadata["chapter"] = title[0].text
        for ptag in subtree.xpath("//html/body/*"):
            for text in ptag.itertext():
                text_chapther += text
            text_chapther += "\n"
    return text_chapther, metadata
def generate_m4b(output_path:str, chapter_paths:List[str], audiobook_metadata:Dict[str,str], chapter_metadata:List[Dict[str,str]]):
    inputs_mp3 = [ffmpeg.input(cp) for cp in chapter_paths]
    joined = ffmpeg.concat(*inputs_mp3, v=0, a=1)
    # Build FFmpeg command for setting metadata
    out = (
        ffmpeg.output(joined, output_path, f='mp4', **{'metadata': audiobook_metadata})
        .output(
            output_path,
            # Set metadata for each chapter
            **{f'metadata:s:a:{i}': chapter for i, chapter in enumerate(chapter_metadata, start=1)}
        )
    )
    out.run()

def get_metadata(root_tree:etree.ElementBase) -> Dict[str,str]:
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
        print(f"Usage: {sys.argv[0]} <input.epub>")
        exit(1)
    input_file_path=sys.argv[1]
    output_file_path=os.path.join(os.path.dirname(__file__), os.path.basename(input_file_path)[:-4]) + ".m4b"
    chapters = []
    metada_output = {}
    ch_metadatas = []
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
            metada_output = get_metadata(tree)
            for idref in tree.xpath("//*[local-name()='package']"
                                    "/*[local-name()='spine']"
                                    "/*[local-name()='itemref']"
                                    "/@idref"):
                output_debug_path= os.path.join(os.path.dirname(output_file_path), f"{idref}.log")
                output_mp3_path  = os.path.join(os.path.dirname(output_file_path), f"{idref}.mp3")
                #TODO get chapter title by toc.nx
                text_chapther, metadata_ch = get_text_from_chapter(tree, idref, content_file_dir_path, guide)
                with open(output_debug_path, "w", encoding="UTF-16") as out_debug_file:
                    out_debug_file.write(text_chapther)
                if len(text_chapther.strip()) > 0:
                    text_chapther = prepocess_text(text_chapther)
                    if generate_audio(text_chapther, output_mp3_path):
                        chapters.append(output_mp3_path)
                        ch_metadatas.append(metadata_ch)
    generate_m4b(output_file_path, chapters, metada_output, chapter_metadata=ch_metadatas)

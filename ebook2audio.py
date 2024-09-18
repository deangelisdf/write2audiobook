#!/usr/bin/python3
"""
file: ebook2audio.py
description: starting from epub file generate a m4b file
Usage example:
    python ebook2audio.py book.epub
"""
import sys
import zipfile
import tempfile
import os
import logging
import codecs
from typing import Dict, Tuple
from lxml   import etree
from backend_audio import m4b
from backend_audio import ffmetadata_generator
from frontend import input_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sys.platform in ('win32', 'cygwin'):
    BACK_END_TTS = "EDGE_TTS"
else:
    BACK_END_TTS = "PYTTS"

def extract_by_epub(epub_path:str, directory_to_extract_path:str) -> None:
    """Unzip the epub file and extract all in a temp directory"""
    logger.debug("Extracting input to temp directory %s.", directory_to_extract_path)
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_path)

def get_guide_epub(root_tree: etree.ElementBase) -> Dict[str,str]:
    """Get information about the guide information, described in content.opf file"""
    guide_res = {}
    for reference in root_tree.xpath("//*[local-name()='package']"
                                "/*[local-name()='guide']"
                                "/*[local-name()='reference']"):
        guide_res[reference.attrib['type']] = reference.attrib['href']
    return guide_res

def prepocess_text(text_in:str) -> str:
    """Remove possible character not audiable"""
    text_out = codecs.decode(bytes(text_in, encoding="utf-8"), encoding="utf-8")
    text_out = text_out.replace('\xa0', '')
    text_out = text_out.replace('\r\n\t', '')
    text_out = text_out.replace('\r\n', '\n')
    return text_out.strip()

def get_text_from_chapter(root_tree:etree._ElementTree,
                          idref_ch :str, content_dir_path:str,
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
            logging.debug("skipping %s", href)
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
    input_file_path, output_file_path = input_tool.get_sys_input(os.path.dirname(__file__))
    chapters = []
    metadata_book_output = {}
    ch_metadatas = []

    m4b.init(BACK_END_TTS)
    with tempfile.TemporaryDirectory() as tmp_dir:
        extract_by_epub(input_file_path, tmp_dir)
        logger.info("Parsing 'container.xml' file.")
        containerFilePath=os.path.join(tmp_dir, "META-INF/container.xml")
        tree = etree.parse(containerFilePath)
        for root_file_path in tree.xpath( "//*[local-name()='container']"
                                        "/*[local-name()='rootfiles']"
                                        "/*[local-name()='rootfile']"
                                        "/@full-path"):
            logger.info("Parsing '%s' file.", root_file_path)
            content_file_path = os.path.join(tmp_dir, root_file_path)
            content_file_dir_path = os.path.dirname(content_file_path)
            tree = etree.parse(content_file_path)
            guide = get_guide_epub(tree)
            metadata_book_output = get_metadata(tree)
            logger.info("Parsed '%s' file.", root_file_path)
            for idref in tree.xpath("//*[local-name()='package']"
                                    "/*[local-name()='spine']"
                                    "/*[local-name()='itemref']"
                                    "/@idref"):
                output_debug_path= os.path.join(os.path.dirname(output_file_path), f"{idref}.log")
                output_mp3_path  = os.path.join(os.path.dirname(output_file_path), f"{idref}.mp3")
                text_chapther, metadata_ch = get_text_from_chapter(tree, idref,
                                                                   content_file_dir_path, guide)
                logger.info("idref %s", idref)
                text_chapther = prepocess_text(text_chapther)
                with open(output_debug_path, "w", encoding="UTF-16") as out_debug_file:
                    out_debug_file.write(text_chapther)
                if m4b.generate_audio(text_chapther, output_mp3_path, backend=BACK_END_TTS):
                    chapters.append(output_mp3_path)
    m4b.close_edge_tts()
    metadata_output = ffmetadata_generator.generate_ffmetadata(chapters)
    with open("ffmetada", "w", encoding="UTF-8") as file_ffmetadata:
        file_ffmetadata.write(metadata_output)
    m4b.generate_m4b(output_file_path, chapters, "ffmetada")

__author__ = "de angelis domenico francesco"

#!/usr/bin/python3
"""
file: [pdf2audio.py](https://github.com/deangelisdf/write2audiobook/blob/main/pdf2audio.py)

description: Convert your pdf to audiobook in MP3 format. <experiment>

Usage example:
    `python pdf2audio.py document.pdf`
"""
import os
import re
import tempfile
import json
from io import BytesIO  # Use BytesIO to create a file-like object
import fitz
from fitz import utils  # PyMuPDF
from fontTools.cffLib import CFFFontSet
from backend_audio import m4b, ffmetadata_generator
from frontend      import input_tool

BACK_END_TTS = m4b.get_back_end_tts()
PATTERN_REFERENCE_STR = r"\[[0-9]+(, [0-9]+)*\]|\([0-9]+(, [a-zA-Z0-9]+)+\)"
REGEX_REFERENCE = re.compile(PATTERN_REFERENCE_STR)

def read_cff(cff_data):
    """Decompile CFF font format"""
    cff_data_io = BytesIO(cff_data)
    cff_font_set = CFFFontSet()
    cff_font_set.decompile(cff_data_io, None)
    return cff_font_set.topDictIndex[0]  # Return the top dictionary

def __filter_family_name(family_name:str)->str:
    family_name = family_name.lower().replace('semibold','').replace('italic','')
    family_name = family_name.replace('medium','').replace('bold','').replace('light','')
    family_name = family_name.replace('book', '')
    return family_name.strip()

def __add_family_name(fonts:dict)->dict:
    result = {}
    for font_name, font in fonts.items():
        cfffont = read_cff(font)
        print(cfffont.FamilyName)
        family_name = __filter_family_name(cfffont.FamilyName)
        result[font_name] = {'family-name': family_name}
    return result

def get_fonts(pdf_doc:utils.pymupdf.Document):
    """..."""
    xref_visited = []
    fonts = {}
    for page in pdf_doc:
        fl = page.get_fonts() # list of fonts of page
        for f in fl:
            xref = f[0] # xref of font
            if xref in xref_visited:
                continue # skip if already processed
            xref_visited.append(xref) # do not process a second time
            # extract font buffer
            basename, ext, _, buffer = pdf_doc.extract_font(xref)
            if ext == "n/a": # is the font extractable?
                continue
            if xref in fonts:
                print(xref, "is already in fonts")
            print(ext)
            fonts[basename] = buffer
    fonts = __add_family_name(fonts)
    return fonts

def filter_reference(text_with_ref:str)->str:
    """remove refence from text
    Args:
        text_with_ref (str): the string contain all the text
    Returns:
        str: the string contain all text without refences"""
    return REGEX_REFERENCE.sub('', text_with_ref)

def get_chapter_text(pdf_doc:utils.pymupdf.Document, pattern_header:str, pattern_footer:str)->list:#pylint: disable=R0914,R1260
    """..."""
    extracted_text = []
    block_prediction = ""
    prev_font = None
    regex_header = re.compile(pattern_header)
    regex_footer = re.compile(pattern_footer)
    for page_num in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    font_name = span["font"]
                    font_size = span["size"]
                    if (prev_font is not None) and (prev_font == (font_name, font_size)):
                        block_prediction += span["text"]
                        continue
                    if regex_footer.match(block_prediction) or regex_header.match(block_prediction):
                        print(block_prediction)
                        block_prediction = ""
                        prev_font = (font_name, font_size)
                        continue
                    extracted_text.append({
                        'txt':filter_reference(block_prediction),
                        'font':font_name,
                        'size':font_size
                    })
                    block_prediction = span["text"]
                    prev_font = (font_name, font_size)
    return extracted_text

def cluster_text(raw_text:list, fonts:dict)->dict:
    """Prototype, it shall organize the text extracted before
    in order to have less possible instance not correlated.
    desiderable: [{chapter title},{chapter text},{chapter title},...]"""
    clustered_text = []
    print(fonts)
    if len(raw_text)<=1:
        return raw_text
    clustered_text.append(raw_text[0])
    for rtext in raw_text[1:]:
        if rtext['size'] == clustered_text[-1]['size'] and\
              rtext['font'] == clustered_text[-1]['font']:
            clustered_text[-1]['txt'] += f" {rtext['txt']}"
        else:
            clustered_text.append(rtext)
    return clustered_text

def get_metadata(pdf_doc):  #pylint: disable=W0613
    """prototype it shall take metadata by the file"""
    return {"title":None, "author":None}

def get_chapters(text_clustered:list)->list:
    """protype it shall return a list of strings
    where each one is a chapter"""
    text_ret = ' '.join([i['txt'] for i in text_clustered])
    return [text_ret]

def main():#pylint: disable=R0914
    """main function"""
    in_file_path, out_file_path, language = input_tool.get_sys_input(os.path.dirname(__file__))
    PATTERN_HEADER = r"arXiv:2310\.03605v3  \[cs.CR\]  29 Nov 2023"  #pylint: disable=C0103
    PATTERN_FOOTER = r"pag. [0-9]+Phenomena Journal \| www\.phenomenajournal.itLuglio-Dicembre 2021 \| Volume 3 \|( Numero [0-9]+ \|)? Ipotesi e metodi di studio"  #pylint: disable=C0103,C0301
    pdf_doc = fitz.open(in_file_path)
    fonts = {}#get_fonts(pdf_doc)
    text = get_chapter_text(pdf_doc, PATTERN_HEADER, PATTERN_FOOTER)
    text = cluster_text(text, fonts)
    with open("test.json", "w", encoding="UTF-8") as outfile:
        outfile.write(json.dumps(text, separators=(",", ":"), indent=4))
    chapters = get_chapters(text)
    metadata = get_metadata(pdf_doc)
    chapter_titles = ["1"]
    chapters_paths = []
    m4b.init(BACK_END_TTS)
    with tempfile.TemporaryDirectory() as tempdir:
        for idx, ch in enumerate(chapters):
            filepath = os.path.join(tempdir, f"{idx}.txt")
            print(ch)
            if m4b.generate_audio(ch, filepath, lang=language, backend=BACK_END_TTS):
                chapters_paths.append(filepath)
    metadata_output = ffmetadata_generator.generate_ffmetadata(chapters_paths,
                                                chapter_titles=chapter_titles,
                                                title=metadata["title"],
                                                author=metadata["author"])
    m4b.generate_m4b(out_file_path, chapters, metadata_output)

if __name__ == "__main__":
    main()

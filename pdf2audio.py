#!/usr/bin/python3
"""
file: [pdf2audio.py](https://github.com/deangelisdf/write2audiobook/blob/main/pdf2audio.py)

description: Convert your pdf to audiobook in MP3 format.

Usage example:
    `python pdf2audio.py document.pdf`
"""
import os
import tempfile
from pathlib import Path
from pypdf   import PdfReader
from backend_audio import m4b, ffmetadata_generator
from frontend      import input_tool

BACK_END_TTS = m4b.get_back_end_tts()

def replace_ligatures(text: str) -> str:
    ligatures = {
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "ﬅ": "ft",
        "ﬆ": "st",
        # "Ꜳ": "AA",
        # "Æ": "AE",
        "ꜳ": "aa",
    }
    for search, replace in ligatures.items():
        text = text.replace(search, replace)
    return text

def __save_page_log(idx_page:int, dirpath:str, text:str):
    log_path = f"{dirpath}/page{idx_page}.log"
    with open(log_path, "w", encoding="UTF-8") as file:
        file.write(text)

def extraction_post_analysis(text:str) -> str:
    """Reduce errors in extraction text by pdf"""
    text = replace_ligatures(text)
    text = text.replace('-\n','')
    return text

def get_metadata(book:PdfReader) -> dict:
    """get useful metadata from PDF"""
    return {"title": book.metadata.title,
            "author": book.metadata.author}

def extract_chapter(text:str, tempdir:str, language:str) -> list:
    """extract chapters and generate audios, to merge in next step"""
    chapters = []
    #if m4b.generate_audio(text_chapther, output_mp3_path,
    #                          lang=language, backend=BACK_END_TTS):
    #    chapters.append(output_mp3_path)
    return chapters

def main():
    """main function"""
    in_file_path, out_file_path, language = input_tool.get_sys_input(os.path.dirname(__file__))
    reader   = PdfReader(in_file_path)
    metadata = get_metadata(reader)
    chapters = []
    with tempfile.TemporaryDirectory() as tempdir:
        for ipage, page in enumerate(reader.pages):
            text = page.extract_text()
            text = extraction_post_analysis(text)
            __save_page_log(ipage, tempdir, text)
        chapters = extract_chapter(text, tempdir, language)
        chapter_titles  = [Path(ch).stem for ch in chapters]
        metadata_output = ffmetadata_generator.generate_ffmetadata(chapters,
                                                            chapter_titles=chapter_titles,
                                                            title=metadata["title"],
                                                            author=metadata["author"])
        with open("ffmetada", "w", encoding="UTF-8") as file_ffmetadata:
            file_ffmetadata.write(metadata_output)
        m4b.generate_m4b(out_file_path, chapters, "ffmetada")

if __name__ == "__main__":
    main()
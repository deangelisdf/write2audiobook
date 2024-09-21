#!/usr/bin/python3
"""Convert your docx to audiobook in M4B format
Example of use:

python docx2audio.py document.docx
"""
import sys
import os
import logging
import asyncio
from typing import List, Tuple, Union
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

TITLE_KEYWORD  = {"it-IT":"TITOLO",   "en":"TITLE"}
CHAPTER_KEYWORD= {"it-IT":"CAPITOLO", "en":"CHAPTER"}
TITLE_TOKENS   = ('Heading 1', 'Title', 'Titolo')
LIST_ITEM_TOKEN= 'List Paragraph'
CHAPTER_TOKEN  = 'Heading 2'
TABLE_VERBOSITY = {
    'en': {
        'start_table': "Starting table reading...",
        'cell_processed': "Processed cell {0}",
        'row_processed': "Processed row {0}",
        'end_table': "Finished table reading."
    },
    'it-IT': {
        'start_table': "Inizio lettura della tabella...",
        'cell_processed': "Cella {0} elaborata",
        'row_processed': "Riga {0} elaborata",
        'end_table': "Lettura della tabella completata."
    }
}


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

def generate_audio(text_in:str, out_mp3_path:str, *, lang:str="it-IT") -> bool:
    """Generating audio using tts apis"""
    ret_val = True
    text_in = text_in.strip()
    if len(text_in) == 0:
        return False
    if BACK_END_TTS == "GTTS":
        ret_val = m4b.generate_audio_gtts(text_in, out_mp3_path, lang=lang)
    elif BACK_END_TTS == "PYTTS":
        ret_val = m4b.generate_audio_pytts(text_in, out_mp3_path, lang=lang)
    elif BACK_END_TTS == "EDGE_TTS":
        loop_audio = asyncio.get_event_loop_policy().get_event_loop()
        #try:
        loop_audio.run_until_complete(m4b.generate_audio_edge_tts(text_in, out_mp3_path, lang=lang))
        #finally:
        #    loop_audio.close()
    return ret_val

def extract_chapters(doc:Document,
                     style_start_chapter_name:Tuple[str] = TITLE_TOKENS
                     ) -> List[Union[Paragraph, Table]]:
    """extract chapters as list of paragraphs and table, the chapter are structured as
    Title (with style like Heading1 and Title) and corpus (other styles)"""
    temp_chapters: List[List[Union[Paragraph, Table]]] = []
    temp:List[Union[Paragraph, Table]] = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            if block.style.name in style_start_chapter_name:
                if len(temp) > 1:
                    temp_chapters.append(temp)
                temp = []
            if len(block.text) == 0:
                continue
        temp.append(block)
    return [i for i in temp_chapters if len(i)>0]

def get_text_from_chapter(chapter_doc:List[Union[Paragraph, Table]],
                          language="it-IT", verbose = False) -> Tuple[str, str]:
    """Generate an intermediate representation in textual version,
    starting from docx format to pure textual, adding sugar context informations."""
    title_str = chapter_doc[0].text
    text = f"{TITLE_KEYWORD[language]}: {title_str}.\n"
    idx_list = 0
    verbosity_msgs = TABLE_VERBOSITY.get(language, TABLE_VERBOSITY['en'])  
    for block in chapter_doc[1:]:
        if isinstance(block, Paragraph):
            if block.style.name == LIST_ITEM_TOKEN:
                text += f"\t{idx_list}: {block.text}.\n"
                idx_list += 1
                continue
            idx_list = 0
            if block.style.name == CHAPTER_TOKEN:
                text += f"\n.\n{CHAPTER_KEYWORD[language]}: "
            text += f"{block.text}\n"
        elif isinstance(block, Table):
            if verbose:
                log_message = verbosity_msgs['start_table']
                logger.info(log_message)
                text += f"{log_message}\n"

            for row_index, row in enumerate(block.rows):
                row_data = []
                for cell_index, cell in enumerate(row.cells):
                    for paragraph in cell.paragraphs:
                        row_data.append(paragraph.text)

                    if verbose:
                        cell_message = verbosity_msgs['cell_processed'].format(cell_index)
                        logger.info(cell_message)
                        text += f"{cell_message}\n"

                row_text = '\t'.join(row_data)
                text += f"{row_text}\n"
                if verbose:
                    row_message = verbosity_msgs['row_processed'].format(row_index)
                    logger.info(row_message)
                    text += f"{row_message}\n"

            if verbose:
                end_message = verbosity_msgs['end_table']
                logger.info(end_message)
                text += f"{end_message}\n"

    return text, title_str


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: {} <input.docx>".format(sys.argv[0]))
        exit(1)
    input_file_path=sys.argv[1]
    output_file_path=os.path.join(os.path.dirname(__file__),
                                  os.path.basename(input_file_path)[:-len(".docx")]) + ".m4b"
    chapters = []
    chapters_path: List[str] = []
    title_list:List[str] = []
    metadata_book_output = {}
    ch_metadatas = []

    m4b.init(BACK_END_TTS)

    document = Document(input_file_path)
    chapters = extract_chapters(document)
    for idref, chapter in enumerate(chapters):
        output_debug_path = f"{input_file_path}.c{idref}.txt"
        output_mp3_path   = f"{input_file_path}.c{idref}.mp3"
        text_chapther, title = get_text_from_chapter(chapter)
        title_list.append(title)
        logger.info("idref {}".format(idref))
        with open(output_debug_path, "w", encoding="UTF-16") as out_debug_file:
            out_debug_file.write(text_chapther)
        if generate_audio(text_chapther, output_mp3_path):
            chapters_path.append(output_mp3_path)
    metadata_output = ffmetadata_generator.generate_ffmetadata(chapters_path,
                                                               chapter_titles=title_list)
    with open("ffmetada", "w", encoding="UTF-8") as file_ffmetadata:
        file_ffmetadata.write(metadata_output)
    m4b.generate_m4b(output_file_path, chapters_path, "ffmetada")
    m4b.close_edge_tts()

__author__ = "de angelis domenico francesco"

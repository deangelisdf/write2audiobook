"""
file: input_file.py
description: handling of external input
"""
import sys
import logging
import argparse
import os
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGE = ["it", "en"]

def get_path(path: str) -> Path:
    """
    parses the path to a file given by user input
    """
    if not os.path.exists(path):
        logger.error("file to read %s does not exist", path)
        sys.exit(1)
    return Path(path)

def get_sys_input(main_path:str, format_output:str="m4b") -> Tuple[str, str, str]:
    """Get input and output path files.

    Arguments:
        main_path: The path of the calling script.
        format_output: The format to save the result file as.

    Returns:
        A tuple of the file supplied by the user at the 
        command-line and the path the result file is saved to.
    """
    argparser = argparse.ArgumentParser(
            usage='usage: %(prog)s <input.docx> <language>',
            prog=sys.argv[0])
    argparser.add_argument('file',
            default=None,
            help='file to be read',
            type=get_path)
    argparser.add_argument('language',
            nargs='?', default="it",
            choices=SUPPORTED_LANGUAGE,
            help='language used by TTS backend')
    argparser.add_argument('--verbose',
            action='store_true', dest='verbose',
            help=('DEBUG mode.'))
    args = argparser.parse_args()
    output_file_name = args.file.stem
    output_file_path = os.path.join(main_path,
                                    output_file_name) + f".{format_output}"
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    logger.debug("%s: read %s language: %s", sys.argv[0],
                 args.file, args.language)
    return args.file, output_file_path, args.language

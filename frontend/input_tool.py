"""
file: input_file.py
description: handling of external input
"""
import sys
import logging
import os
from pathlib import Path
from typing import Tuple

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def get_sys_input(main_path:str, format_output:str="m4b") -> Tuple[str, str]:
    """Get input and output path files.

    Arguments:
        main_path: The path of the calling script.
        format_output: The format to save the result file as.

    Returns:
        A tuple of the file supplied by the user at the 
        command-line and the path the result file is saved to.
    """
    if len(sys.argv) != 2:
        logger.error("Usage: %s <input.docx>",sys.argv[0])
        sys.exit(1)
    input_file_path  = sys.argv[1]
    output_file_name = Path(input_file_path).stem
    output_file_path = os.path.join(main_path,
                                    output_file_name) + f".{format_output}"
    return input_file_path, output_file_path

#!/usr/bin/env python3
# Modified from the original by David C Ellis

# Original notice
# Author: Theeko74
# Contributor(s): skjerns
# Oct, 2021
# MIT license -- free to use as you want, cheers.


"""
Simple python wrapper script to use ghoscript function to compress PDF files.

Compression levels:
    0: default
    1: prepress
    2: printer
    3: ebook
    4: screen
"""

import subprocess
import os
import shutil

from pathlib import Path

from ..exceptions import FileTypeError


def compress_pdf(input_path, output_path, power=2):
    """
    Compress PDF using ghostscript through subprocess
    """
    # Convert to pathlib
    input_path = Path(input_path)
    output_path = Path(output_path)

    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen",
    }

    # Basic controls
    # Check if valid path
    if not input_path.is_file():
        raise FileNotFoundError(f"Could not find file {input_path}")

    # Check if file is a PDF by extension
    if input_path.suffix != ".pdf":
        raise FileTypeError("Incorrect file type.")

    gs = get_ghostscript_path()

    # Perform the compression
    result = subprocess.run(
        [
            gs,
            "-sDEVICE=pdfwrite",
            f"-dPDFSETTINGS={quality[power]}",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path,
        ]
    )

    return result


def get_ghostscript_path():
    gs_names = ["gs", "gswin32", "gswin64"]
    for name in gs_names:
        pth = shutil.which(name)
        if pth:
            return pth

    # If not on path, search program files
    base_dir = Path(os.environ["ProgramFiles"]) / "gs"
    for pth in sorted(base_dir.iterdir(), reverse=True):
        if pth.is_dir():
            for name in gs_names:
                gs_file = pth / "bin" / f"{name}.exe"
                if gs_file.exists():
                    return str(gs_file)

    raise FileNotFoundError(
        f'No GhostScript executable was found on path ({"/".join(gs_names)})'
    )

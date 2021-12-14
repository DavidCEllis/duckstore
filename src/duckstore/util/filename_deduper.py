"""
Prevent Filename Clashes
"""
import secrets
from datetime import datetime
from pathlib import Path


def prepare_storepath(pth):
    """
    Prepare filename for server
    For our usecase we're going to append the date uploaded to the file.
    If there's still a clash add a random token until there is no longer a clash.

    :param pth: input filename
    :return:
    """
    pth = Path(pth)
    stamp = datetime.today().strftime("%Y-%m-%d")
    pth = pth.with_stem(f"{pth.stem}_{stamp}")

    while pth.is_file():
        stem = f"{pth.stem}_{secrets.token_hex(4)}"
        pth = pth.with_stem(stem)
    return pth

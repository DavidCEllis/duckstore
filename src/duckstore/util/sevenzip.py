"""
Handle the external py7zr library.

This should do what is expected in every case. If I have to replace py7zr at some point
with a different external library this should make it easier to do by concentrating it here.
"""
from pathlib import Path
from py7zr import SevenZipFile


def extract_archive(archive, destination, password=None):
    destination = Path(destination)
    destination.mkdir(exist_ok=True)

    with SevenZipFile(archive, mode='r', password=password) as f:
        f.extractall(destination)


def create_archive(source, archive, password=None, overwrite=False):
    archive = Path(archive).resolve()
    source = Path(source).resolve()
    if not overwrite and archive.exists():
        raise FileExistsError("Archive file already exists")

    with SevenZipFile(archive, mode='w', password=password) as f:
        f.writeall(source)

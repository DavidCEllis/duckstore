"""
tkinter file dialog shortcuts.
"""
from contextlib import contextmanager

from pathlib import Path
from tkinter import Tk, filedialog


@contextmanager
def dialog_handler():
    """Short decorator to create, hide and destroy the necessary Tk root"""
    root = Tk()
    root.withdraw()
    try:
        yield
    finally:
        root.destroy()


@dialog_handler()
def get_folder_dialog(initialdir="."):
    folder = filedialog.askdirectory(
        initialdir=initialdir,
        title="Select a duckstore archive folder",
    )

    if folder:
        return Path(folder)
    else:
        return None


@dialog_handler()
def get_archive_dialog(initialdir="."):
    archive_file = filedialog.askopenfilename(
        initialdir=initialdir,
        title="Select a duckstore archive file",
        filetypes=(("7zip archives", "*.7z"),),
    )

    if archive_file:
        return Path(archive_file)
    else:
        return None

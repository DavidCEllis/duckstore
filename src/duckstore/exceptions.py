"""
Custom exceptions
"""


class DatabaseNotFoundError(Exception):
    pass


class FileTypeError(Exception):
    """Error for attempting to compress the wrong file type"""
    pass

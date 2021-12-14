import json
from pathlib import Path


secrets_file = (Path(__file__).parents[2] / '.secrets').resolve()
db_name = "duckstore.db"
store_name = "store"


class Config:
    try:
        _secrets = json.loads(secrets_file.read_text())
    except FileNotFoundError:
        SECRET_KEY = None
    else:
        SECRET_KEY = _secrets['SECRET_KEY']

    STORE_PATH = None
    STORE_NAME = store_name
    DB_NAME = db_name
    MAX_CONTENT_LENGTH = 100*1024**2
    WTF_CSRF_ENABLED = True
    PRETTIFY = True


def make_config(configname, store_path):
    new_config = type(
        configname,
        (Config, ),
        {"STORE_PATH": store_path}
    )

    return new_config

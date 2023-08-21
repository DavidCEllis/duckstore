import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from duckstore.app import create_app
from duckstore.database import create_db
from duckstore.config import db_name

src_folder = Path("./src").resolve()
sys.path.insert(0, str(src_folder))

test_folder = Path(__file__).parent.resolve()


@pytest.fixture
def db_folder():
    store_base = test_folder / "stores"
    store_base.mkdir(exist_ok=True)

    tempdir = TemporaryDirectory(dir=store_base)
    folder = tempdir.name
    folder_path = Path(folder)
    create_db(folder_path / db_name, replace=False)
    yield folder

    tempdir.cleanup()


@pytest.fixture
def client():
    """
    Provide the flask test client.
    
    :return:
    """
    store_base = test_folder / "stores"
    store_base.mkdir(exist_ok=True)  # Make the stores folder if it doesn't exist

    with TemporaryDirectory(dir=store_base) as folder:
        app = create_app(folder_path=folder, create=True)

        with app.test_client() as client:
            yield client

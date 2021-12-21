import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from duckstore.app import create_app

src_folder = Path("./src").resolve()
sys.path.insert(0, str(src_folder))

test_folder = Path(__file__).resolve()


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

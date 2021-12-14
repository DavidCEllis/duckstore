from pathlib import Path

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_pretty import Prettify

from .config import make_config, db_name
from .database import bind_session, cleanup_session, create_db


def create_app(folder_path=".", create=False):
    """
    Create an application instance from a duckstore folder

    :param folder_path: Path to duckstore folder
    :param create: Create a new store in the folder
    :return: flask app
    """

    folder_path = Path(folder_path).resolve()
    config = make_config("AppConfig", folder_path)
    app = Flask(__name__)
    app.config.from_object(config)

    # Set up the session
    db_path = folder_path / db_name
    store_path = folder_path / config.STORE_NAME
    store_path.mkdir(exist_ok=True)
    if not db_path.exists():
        if create:
            create_db(db_path)

        else:
            raise FileNotFoundError("Database duckstore.db file not found in database")

    bind_session(db_path)

    Bootstrap(app)
    Prettify(app)

    from . import views

    app.register_blueprint(views.duckstore)

    app.teardown_appcontext(cleanup_session)

    return app

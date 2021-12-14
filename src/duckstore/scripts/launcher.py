from code import InteractiveConsole
from pathlib import Path
import sys

import click


from duckstore.config import db_name
from duckstore.util import get_archive_dialog, get_folder_dialog, extract_archive
from duckstore.app import create_app


@click.command()
@click.option(
    "--source",
    type=click.Path(resolve_path=True, path_type=Path, file_okay=True, exists=True),
    help=".7z Archive source for initialization if needed.",
)
@click.option(
    "--folder",
    type=click.Path(resolve_path=True, path_type=Path, dir_okay=True, file_okay=False),
    help="Duckstore folder (or destination for archive source).",
)
@click.option("--create", is_flag=True, help="Create a new store at the folder location.")
@click.option("--shell", is_flag=True, help="Launch into a shell instead of the web server.")
@click.option("--password", help="Password if the 7z archive is encrypted.")
def launch(folder, create, source, shell, password):
    if folder:
        db_path = folder / db_name
    else:
        # If there's a duckstore.db in the working directory use that, otherwise ask
        folder = Path(".")
        db_path = folder / db_name

        if not db_path.is_file():
            folder = get_folder_dialog()
            if not folder:
                click.echo("Folder not selected - Exiting.")
                sys.exit(1)
            db_path = folder / db_name

    if db_path.is_file():
        # If a database is found in the folder, just load that.
        db_path = db_path.resolve()
        click.echo(f"Database found at {db_path}. Loading from folder.")
    else:
        # Otherwise we have the option of creating a new database or loading from an archive.
        click.echo(f"Database not found at {db_path}.")
        if create:
            click.echo(f"New Database will be created at {db_path}")
        elif source:
            click.echo(f"Extracting store from {source}")
            if not password:
                password = click.prompt("Password: ", hide_input=True, default="")
                if password == "":
                    password = None
            extract_archive(source, folder, password)
            click.echo(f"Extracted project to {folder}")
        else:
            choice = click.prompt(
                "Create new duckstore or load from archive: ",
                type=click.Choice(["new", "load"]),
                default="load"
            )
            if choice == "new":
                create = True
                click.echo(f"New Database will be created at {db_path}")
            else:
                # Chosen to load from source
                source = get_archive_dialog()
                if not source:
                    click.echo("Source not selected, Exiting.")
                    sys.exit(1)
                click.echo(f"Extracting store from {source}")
                password = click.prompt("Password: ", hide_input=True, default="")
                if password == "":
                    password = None
                extract_archive(source, folder, password)
                click.echo(f"Extracted project to {folder}")

    if shell:
        # These imports are done to put things in locals for easier shell usage
        # noinspection PyUnresolvedReferences
        from duckstore.database.models import File, Source, Tag, Document
        # noinspection PyUnresolvedReferences
        from duckstore.database import db_session, bind_session
        # noinspection PyUnresolvedReferences
        from sqlalchemy import select

        if not db_path.is_file():
            if create:
                from duckstore.database import create_db
                create_db(db_path)
            else:
                raise FileNotFoundError(f"Database file {db_path} does not exist.")

        bind_session(db_path)
        console = InteractiveConsole(locals=locals())
        console.interact()
    else:
        app = create_app(folder, create=create)
        app.run()


if __name__ == "__main__":
    launch()

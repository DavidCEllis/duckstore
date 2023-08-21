"""
Test the launcher runs the correct commands given the correct input
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from duckstore.config import db_name
from duckstore.scripts.launcher import launch


launcher_mod = "duckstore.scripts.launcher"


def test_launch_loads_db(db_folder):
    runner = CliRunner()

    db_folder_path = Path(db_folder)
    db_path = db_folder_path / db_name

    assert db_path.is_file()

    with (patch(f"{launcher_mod}.create_app") as mock,
          patch.object(Path, "cwd") as cwd_mock):

        cwd_mock.return_value = db_folder_path
        run_mock = mock.return_value

        result = runner.invoke(launch)  # noqa

        mock.assert_called_once_with(db_folder_path, create=False)
        run_mock.run.assert_called()

    assert result.exit_code == 0
    assert result.output == (
        f"Database found at {db_path}. Loading from folder.\n"
    )


def test_launch_nofolder_selected():
    """
    Test the launcher exits as intended if not given a folder
    :return:
    """

    runner = CliRunner()

    with patch(f"{launcher_mod}.get_folder_dialog") as mock:
        mock.return_value = False

        result = runner.invoke(launch, args=[])  # noqa

    assert result.exit_code == 1
    assert result.output == "Folder not selected - Exiting.\n"

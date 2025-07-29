import pathlib
from unittest.mock import patch

import click
import pytest

from src.helpers.docs_dir_guard import ensure_docs_directory_exists


def test_ensure_docs_directory_exists_already_exists(tmp_path: pathlib.Path) -> None:
    """Test when the docs directory already exists."""
    # tmp_path is already created by pytest fixture
    ensure_docs_directory_exists(tmp_path)
    assert tmp_path.exists()


def test_ensure_docs_directory_exists_create_confirmed(tmp_path: pathlib.Path) -> None:
    """Test creating the docs directory when confirmed."""
    non_existent_dir = tmp_path / "new_docs"
    with patch("click.confirm", return_value=True):
        ensure_docs_directory_exists(non_existent_dir)
    assert non_existent_dir.exists()


def test_ensure_docs_directory_exists_create_cancelled(tmp_path: pathlib.Path) -> None:
    """Test cancelling the creation of the docs directory."""
    non_existent_dir = tmp_path / "new_docs"
    with patch("click.confirm", return_value=False), pytest.raises(click.Abort):
        ensure_docs_directory_exists(non_existent_dir)
    assert not non_existent_dir.exists()


def test_ensure_docs_directory_exists_permission_error(tmp_path: pathlib.Path) -> None:
    """Test PermissionError during directory creation."""
    non_existent_dir = tmp_path / "new_docs"

    with (
        patch("click.confirm", return_value=True),
        patch("pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")),
    ):
        with pytest.raises(click.ClickException) as excinfo:
            ensure_docs_directory_exists(non_existent_dir)
        assert "insufficient permissions" in str(excinfo.value)


def test_ensure_docs_directory_exists_file_not_found_error(
    tmp_path: pathlib.Path,
) -> None:
    """Test FileNotFoundError when parent directory does not exist."""
    non_existent_parent = tmp_path / "non_existent_parent"
    non_existent_dir = non_existent_parent / "new_docs"

    with patch("click.confirm", return_value=True):
        with pytest.raises(click.ClickException) as excinfo:
            ensure_docs_directory_exists(non_existent_dir)
        assert "parent directory does not exist" in str(excinfo.value)


def test_ensure_docs_directory_exists_generic_exception(tmp_path: pathlib.Path) -> None:
    """Test generic Exception during directory creation."""
    non_existent_dir = tmp_path / "new_docs"
    with (
        patch("click.confirm", return_value=True),
        patch("pathlib.Path.mkdir", side_effect=Exception("Generic mkdir error")),
    ):
        with pytest.raises(click.ClickException) as excinfo:
            ensure_docs_directory_exists(non_existent_dir)
        assert "Error creating docs directory" in str(excinfo.value)

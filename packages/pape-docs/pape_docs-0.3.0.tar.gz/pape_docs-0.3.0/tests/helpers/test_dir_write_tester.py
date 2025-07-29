import pathlib
from unittest.mock import patch

import click
import pytest

from src.helpers.dir_write_tester import perform_write_test


def test_perform_write_test_success(tmp_path: pathlib.Path) -> None:
    """Test successful write and delete."""
    perform_write_test(in_dir=tmp_path)
    assert not (tmp_path / ".pape-docs-write-test.tmp").exists()


def test_perform_write_test_file_not_found_error(tmp_path: pathlib.Path) -> None:
    """Test FileNotFoundError when directory does not exist."""
    non_existent_dir = tmp_path / "non_existent_dir"
    with pytest.raises(click.ClickException) as excinfo:
        perform_write_test(in_dir=non_existent_dir)
    assert "does not exist or is not accessible" in str(excinfo.value)


def test_perform_write_test_os_error_on_write(tmp_path: pathlib.Path) -> None:
    """Test OSError during file write with a permission error of aa read-only directory."""
    original_permissions = tmp_path.stat().st_mode
    tmp_path.chmod(0o444)  # Read-only permissions

    with pytest.raises(click.ClickException) as excinfo:
        perform_write_test(in_dir=tmp_path)
    assert "Cannot write to docs directory" in str(excinfo.value)

    # Restore permissions for cleanup
    tmp_path.chmod(original_permissions)


def test_perform_write_test_generic_exception_on_write(tmp_path: pathlib.Path) -> None:
    """Test generic Exception during file write."""
    with patch("pathlib.Path.write_text", side_effect=Exception("Generic write error")):
        with pytest.raises(click.ClickException) as excinfo:
            perform_write_test(in_dir=tmp_path)
        assert "Error writing to docs directory" in str(excinfo.value)


def test_perform_write_test_exception_on_unlink(tmp_path: pathlib.Path) -> None:
    """Test Exception during file unlink."""
    # Create the test file first
    test_file = tmp_path / ".pape-docs-write-test.tmp"
    test_file.write_text("test")

    with patch("pathlib.Path.unlink", side_effect=Exception("Generic unlink error")):
        with pytest.raises(click.ClickException) as excinfo:
            perform_write_test(in_dir=tmp_path)
        assert "Error deleting temporary file" in str(excinfo.value)

    # Ensure the file still exists after the failed unlink attempt
    assert test_file.exists()

import pathlib
import subprocess
import sys
from collections.abc import Generator
from unittest import mock

import click
import pytest
from click.testing import CliRunner

from src import new_doc


@pytest.fixture
def runner() -> CliRunner:
    """Make a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Provide a temporary directory for testing."""
    return tmp_path


@pytest.fixture(autouse=True)
def mock_pape_docs_dir_finder() -> Generator[mock.MagicMock | mock.AsyncMock]:
    """
    Mock PapeDocsDirectoryFinder class to control its behavior.

    By default, the search method returns None, simulating no docs directory found.
    """
    with mock.patch("src.new_doc.pape_docs_dir_finder.PapeDocsDirectoryFinder") as _mock_class:
        _mock_class.return_value.search.return_value = None
        yield _mock_class


@pytest.fixture(autouse=True)
def mock_os_getenv() -> Generator[mock.MagicMock | mock.AsyncMock]:
    """
    Mock os.getenv to control the PAPE_DOCS_DIR environment variable.

    By default, it returns None, simulating the variable not being set.
    """
    with mock.patch("src.new_doc.os.getenv", return_value=None) as _mock:
        yield _mock


@pytest.fixture(autouse=True)
def mock_ensure_docs_directory_exists() -> Generator[mock.MagicMock | mock.AsyncMock]:
    """Mock docs_dir_guard.ensure_docs_directory_exists."""
    with mock.patch("src.new_doc.docs_dir_guard.ensure_docs_directory_exists") as _mock:
        yield _mock


@pytest.fixture(autouse=True)
def mock_perform_write_test() -> Generator[mock.MagicMock | mock.AsyncMock]:
    """Mock dir_write_tester.perform_write_test."""
    with mock.patch("src.new_doc.dir_write_tester.perform_write_test") as _mock:
        yield _mock


@pytest.fixture(autouse=True)
def mock_get_sanitized_file_name_part() -> Generator[mock.MagicMock | mock.AsyncMock]:
    """
    Mock file_name_part_retriever.get_sanitized_file_name_part.

    By default, it returns the initial_value passed to it.
    """
    with mock.patch(
        "src.new_doc.file_name_part_retriever.get_sanitized_file_name_part",
        side_effect=lambda initial_value, **_kwargs: initial_value,
    ) as _mock:
        yield _mock


@pytest.fixture(autouse=True)
def mock_generate_document_content() -> Generator[mock.MagicMock | mock.AsyncMock]:
    """Mock template_loader.generate_document_content."""
    with mock.patch(
        "src.new_doc.template_loader.generate_document_content",
        return_value="Generated content",
    ) as _mock:
        yield _mock


class TestGetDocsDirectory:
    """Tests for the _get_docs_directory function."""

    def test_from_env_variable(
        self,
        mock_os_getenv: mock.MagicMock | mock.AsyncMock,
        temp_dir: pathlib.Path,
    ) -> None:
        """It returns the path from PAPE_DOCS_DIR environment variable."""
        mock_os_getenv.return_value = str(temp_dir / "env_docs")
        result = new_doc._get_docs_directory()
        assert result == temp_dir / "env_docs"
        mock_os_getenv.assert_called_once_with("PAPE_DOCS_DIR")

    def test_from_finder_search(
        self,
        mock_pape_docs_dir_finder: mock.MagicMock | mock.AsyncMock,
        mock_os_getenv: mock.MagicMock | mock.AsyncMock,
        temp_dir: pathlib.Path,
    ) -> None:
        """It returns the path from `PapeDocsDirectoryFinder.search` if env var is not set."""
        mock_os_getenv.return_value = None  # Ensure env var is not set
        mock_pape_docs_dir_finder.return_value.search.return_value = temp_dir / "finder_docs"
        result = new_doc._get_docs_directory()
        assert result == temp_dir / "finder_docs"
        mock_pape_docs_dir_finder.return_value.search.assert_called_once_with(
            starting_at_directory=pathlib.Path.cwd(),
        )

    def test_no_docs_directory_found(self) -> None:
        """It returns None if no docs directory is found."""
        result = new_doc._get_docs_directory()
        assert result is None


class TestProcessInvocationArguments:
    """Tests for the _process_invocation_arguments function."""

    def test_all_args_provided(self) -> None:
        """It returns sanitized values when all arguments are provided."""
        short_title, priority, doc_type = new_doc._process_invocation_arguments(
            "My Title",
            "001",
            "RFC",
        )
        assert short_title == "My Title"
        assert priority == "001"
        assert doc_type == "RFC"

    def test_doc_type_prompted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """It prompts for doc_type if not provided."""
        monkeypatch.setattr(click, "prompt", lambda *_args, **_kwargs: "Note")
        short_title, priority, doc_type = new_doc._process_invocation_arguments(
            "My Title",
            "001",
            None,
        )
        assert short_title == "My Title"
        assert priority == "001"
        assert doc_type == "Note"

    def test_doc_type_prompt_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """It uses default for doc_type prompt if user enters nothing."""
        monkeypatch.setattr(click, "prompt", lambda *_args, **_kwargs: None)
        short_title, priority, doc_type = new_doc._process_invocation_arguments(
            "My Title",
            "001",
            None,
        )
        assert short_title == "My Title"
        assert priority == "001"
        assert doc_type is None


class TestNewDocCommand:
    """Tests for the new_doc_command CLI command."""

    def test_no_docs_directory_error(
        self,
        runner: CliRunner,
        mock_os_getenv: mock.MagicMock | mock.AsyncMock,
        mock_pape_docs_dir_finder: mock.MagicMock | mock.AsyncMock,
    ) -> None:
        """It raises ClickException if no docs directory is found."""
        mock_os_getenv.return_value = None
        mock_pape_docs_dir_finder.return_value.search.return_value = None

        result = runner.invoke(new_doc.new_doc_command, ["test-title"])
        assert result.exit_code == 1
        assert "The script detected no PAPE_DOCS_DIR environment variable" in result.output

    def test_successful_doc_creation(
        self,
        runner: CliRunner,
        temp_dir: pathlib.Path,
        mock_os_getenv: mock.MagicMock | mock.AsyncMock,
        mock_ensure_docs_directory_exists: mock.MagicMock | mock.AsyncMock,
        mock_perform_write_test: mock.MagicMock | mock.AsyncMock,
        mock_get_sanitized_file_name_part: mock.MagicMock | mock.AsyncMock,
        mock_generate_document_content: mock.MagicMock | mock.AsyncMock,
    ) -> None:
        """It successfully creates a new document."""
        mock_os_getenv.return_value = str(temp_dir / "my_docs")
        (temp_dir / "my_docs").mkdir()  # Simulate docs dir creation

        result = runner.invoke(
            new_doc.new_doc_command,
            ["my-test-doc", "--priority", "001", "--doc-type", "Note"],
        )

        assert result.exit_code == 0
        expected_path = temp_dir / "my_docs" / "001 my-test-doc.md"
        assert f"✓ Document created successfully at {expected_path}" in result.output
        assert expected_path.exists()
        assert expected_path.read_text() == "Generated content"

        mock_ensure_docs_directory_exists.assert_called_once_with(temp_dir / "my_docs")
        mock_perform_write_test.assert_called_once_with(in_dir=temp_dir / "my_docs")
        mock_get_sanitized_file_name_part.assert_any_call(
            argument_name="short title",
            initial_value="my-test-doc",
        )
        mock_get_sanitized_file_name_part.assert_any_call(
            argument_name="priority",
            initial_value="001",
            baseline_default="????",
        )
        mock_generate_document_content.assert_called_once_with(doc_type="Note")

    @pytest.mark.usefixtures(
        "mock_ensure_docs_directory_exists",
        "mock_perform_write_test",
        "mock_get_sanitized_file_name_part",
        "mock_generate_document_content",
    )
    def test_file_exists_and_overwrite_confirmed(
        self,
        runner: CliRunner,
        temp_dir: pathlib.Path,
        mock_os_getenv: mock.MagicMock | mock.AsyncMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """It overwrites an existing file if confirmed."""
        mock_os_getenv.return_value = str(temp_dir / "my_docs")
        docs_dir = temp_dir / "my_docs"
        docs_dir.mkdir()
        existing_file = docs_dir / "001 existing-doc.md"
        existing_file.write_text("Old content")

        mock_confirm = mock.MagicMock(return_value=True)
        monkeypatch.setattr(click, "confirm", mock_confirm)

        result = runner.invoke(
            new_doc.new_doc_command,
            ["existing-doc", "--priority", "001", "--doc-type", "note"],
        )

        assert result.exit_code == 0
        mock_confirm.assert_called_once()
        assert "Overwrite it?" in mock_confirm.call_args.args[0]
        assert existing_file.read_text() == "Generated content"
        assert f"✓ Document created successfully at {existing_file}" in result.output

    @pytest.mark.usefixtures(
        "mock_ensure_docs_directory_exists",
        "mock_perform_write_test",
        "mock_get_sanitized_file_name_part",
    )
    def test_file_exists_and_overwrite_cancelled(
        self,
        runner: CliRunner,
        temp_dir: pathlib.Path,
        mock_os_getenv: mock.MagicMock | mock.AsyncMock,
        mock_generate_document_content: mock.MagicMock | mock.AsyncMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """It cancels operation if overwrite is not confirmed."""
        mock_os_getenv.return_value = str(temp_dir / "my_docs")
        docs_dir = temp_dir / "my_docs"
        docs_dir.mkdir()
        existing_file = docs_dir / "001 existing-doc.md"
        existing_file.write_text("Old content")

        mock_confirm = mock.MagicMock(return_value=False)
        monkeypatch.setattr(click, "confirm", mock_confirm)

        result = runner.invoke(
            new_doc.new_doc_command,
            ["existing-doc", "--priority", "001", "--doc-type", "Note"],
        )

        assert result.exit_code == 0
        mock_confirm.assert_called_once()
        assert "Overwrite it?" in mock_confirm.call_args.args[0]
        assert "Operation cancelled." in result.output
        assert existing_file.read_text() == "Old content"  # Content should not change
        mock_generate_document_content.assert_not_called()

    def test_main_entry_point_coverage(
        self,
        runner: CliRunner,
        mock_os_getenv: mock.MagicMock | mock.AsyncMock,
        mock_pape_docs_dir_finder: mock.MagicMock | mock.AsyncMock,
    ) -> None:
        """It covers the main entry point by simulating script execution."""
        # Simulate no docs directory found to trigger the ClickException path
        # This ensures the main() function is called and the cli() is invoked,
        # leading to the exception and covering the entry point.
        mock_os_getenv.return_value = None
        mock_pape_docs_dir_finder.return_value.search.return_value = None

        result = runner.invoke(new_doc.cli, ["new", "test-title"])
        assert result.exit_code == 1
        assert "The script detected no PAPE_DOCS_DIR environment variable" in result.output


@pytest.mark.usefixtures("runner")
def test_main_invokes_cli() -> None:
    """Test that main function invokes the cli group."""
    with mock.patch.object(new_doc, "cli") as mock_cli:
        new_doc.main()
        mock_cli.assert_called_once()


def test_script_main_entry_point(
    temp_dir: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """It covers the main entry point by executing the script as a subprocess."""
    docs_dir = temp_dir / "my_subprocess_docs"
    docs_dir.mkdir()

    # Set the environment variable for the subprocess
    monkeypatch.setenv("PAPE_DOCS_DIR", str(docs_dir))

    # Execute the script as a subprocess
    # We need to use sys.executable to ensure the correct python interpreter is used
    # and pass the script path as an argument.

    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            str(pathlib.Path("src") / "new_doc.py"),
            "new",
            "test-subprocess-doc",
            "--priority",
            "007",
            "--doc-type",
            "Test",
        ],
        capture_output=True,
        text=True,
        check=False,  # Do not raise an exception for non-zero exit codes
    )

    assert result.returncode == 0
    expected_path = docs_dir / "007 test-subprocess-doc.md"
    assert f"✓ Document created successfully at {expected_path}" in result.stdout
    assert expected_path.exists()

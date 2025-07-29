from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import click
import pytest

from src.helpers.template_loader import TemplateLoader, generate_document_content


@pytest.fixture
def mock_templates_dir(tmp_path: Path) -> Path:
    """Fixture to create a temporary templates directory."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "doc.md").write_text(
        "Template content <!-- date --> <!-- doc type --> A(n) doc.",
    )
    return templates_dir


@pytest.fixture
def mock_pape_utilities_ap_style_date_string() -> Generator[MagicMock | AsyncMock, Any]:
    """Mock pape.utilities.ap_style_date_string to return a consistent date string."""
    with patch(
        "pape.utilities.ap_style_date_string",
        return_value="July 22, 2025",
    ) as mock_date_string:
        yield mock_date_string


@pytest.fixture
def mock_datetime_now() -> Generator[MagicMock | AsyncMock, Any]:
    """Mock datetime.now to return a consistent datetime object."""
    with patch("datetime.now") as mock_now:
        mock_now.return_value = datetime(2025, 7, 22, 10, 30, 0, tzinfo=UTC)
        yield mock_now


@pytest.fixture
def mock_tzlocal_get_localzone() -> Generator[MagicMock | AsyncMock, Any]:
    """Mock tzlocal.get_localzone."""
    with patch("tzlocal.get_localzone") as mock_get_localzone:
        mock_get_localzone.return_value = MagicMock()  # Return a mock timezone object
        yield mock_get_localzone


def test_template_loader_init(mock_templates_dir: Path) -> None:
    """Test TemplateLoader initialization."""
    loader = TemplateLoader(templates_dir=mock_templates_dir)
    assert loader.templates_dir == mock_templates_dir


@pytest.mark.usefixtures("mock_pape_utilities_ap_style_date_string")
def test_generate_document_content_class_method_no_doc_type(
    mock_templates_dir: Path,
) -> None:
    """Test generate_document_content class method with no doc_type."""
    loader = TemplateLoader(templates_dir=mock_templates_dir)
    content = loader.generate_document_content()
    assert "Template content July 22, 2025 <!-- doc type --> A(n) doc." in content


@pytest.mark.usefixtures("mock_pape_utilities_ap_style_date_string")
def test_generate_document_content_class_method_consonant_doc_type(
    mock_templates_dir: Path,
) -> None:
    """Test generate_document_content class method with a consonant doc_type."""
    loader = TemplateLoader(templates_dir=mock_templates_dir)
    content = loader.generate_document_content(with_doc_type="Feature")
    assert "Template content July 22, 2025 Feature A doc." in content


@pytest.mark.usefixtures("mock_pape_utilities_ap_style_date_string")
def test_generate_document_content_class_method_vowel_doc_type(
    mock_templates_dir: Path,
) -> None:
    """Test generate_document_content class method with a vowel doc_type."""
    loader = TemplateLoader(templates_dir=mock_templates_dir)
    content = loader.generate_document_content(with_doc_type="Epic")
    assert "Template content July 22, 2025 Epic An doc." in content


def test_generate_document_content_class_method_template_not_found(
    mock_templates_dir: Path,
) -> None:
    """Test generate_document_content class method when template file is not found."""
    # Remove the doc.md file to simulate it not existing
    (mock_templates_dir / "doc.md").unlink()

    loader = TemplateLoader(templates_dir=mock_templates_dir)
    with pytest.raises(click.Abort):
        loader.generate_document_content()


@pytest.mark.usefixtures("mock_pape_utilities_ap_style_date_string")
def test_generate_document_content_convenience_function_no_doc_type(
    mock_templates_dir: Path,
) -> None:
    """Test generate_document_content convenience function with no doc_type."""
    content = generate_document_content(templates_dir=mock_templates_dir)
    assert "Template content July 22, 2025 <!-- doc type --> A(n) doc." in content


@pytest.mark.usefixtures("mock_pape_utilities_ap_style_date_string")
def test_generate_document_content_convenience_function_consonant_doc_type(
    mock_templates_dir: Path,
) -> None:
    """Test generate_document_content convenience function with a consonant doc_type."""
    content = generate_document_content(
        templates_dir=mock_templates_dir, doc_type="Story",
    )
    assert "Template content July 22, 2025 Story A doc." in content


@pytest.mark.usefixtures("mock_pape_utilities_ap_style_date_string")
def test_generate_document_content_convenience_function_vowel_doc_type(
    mock_templates_dir: Path,
) -> None:
    """Test generate_document_content convenience function with a vowel doc_type."""
    content = generate_document_content(
        templates_dir=mock_templates_dir, doc_type="Idea",
    )
    assert "Template content July 22, 2025 Idea An doc." in content

from pathlib import Path

import pytest

from src.helpers.pape_docs_dir_finder import PapeDocsDirectoryFinder


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def finder() -> PapeDocsDirectoryFinder:
    """Provide an instance of PapeDocsDirectoryFinder."""
    return PapeDocsDirectoryFinder()


def test_find_from_explicit_definition_env_file(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we find the docs directory defined in a .env file."""
    # Create a .env file in the temporary directory
    env_file_path = temp_dir / ".env"
    docs_dir_name = "my_docs"
    env_file_path.write_text(f"PAPE_DOCS_DIR={docs_dir_name}\n")

    expected_path = temp_dir / docs_dir_name
    result = finder.find_from_explicit_definition(for_directory=temp_dir)

    assert result == expected_path


def test_find_from_explicit_definition_dot_pape_docs_file(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we find the docs directory when defined in a .pape-docs file."""
    dot_pape_docs_path = temp_dir / ".pape-docs"
    docs_dir_name = "another_docs"
    dot_pape_docs_path.write_text(docs_dir_name)

    expected_path = temp_dir / docs_dir_name
    result = finder.find_from_explicit_definition(for_directory=temp_dir)

    assert result == expected_path


def test_find_from_explicit_definition_pyproject_toml_file(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we correctly find the docs directory when defined in a pyproject.toml file."""
    pyproject_path = temp_dir / "pyproject.toml"
    docs_dir_name = "project_docs"
    pyproject_path.write_text(f'[tool."pape-docs"]\ndocs-dir = "{docs_dir_name}"\n')

    expected_path = temp_dir / docs_dir_name
    result = finder.find_from_explicit_definition(for_directory=temp_dir)

    assert result == expected_path


def test_find_from_explicit_definition_no_definition(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we return None when no explicit definition is found."""
    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result is None


def test_find_from_explicit_definition_in_parent_directory(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we find the docs directory in a parent directory."""
    parent_dir = temp_dir / "parent"
    child_dir = parent_dir / "child"
    child_dir.mkdir(parents=True)

    env_file_path = parent_dir / ".env"
    docs_dir_name = "parent_docs"
    env_file_path.write_text(f"PAPE_DOCS_DIR={docs_dir_name}\n")

    expected_path = parent_dir / docs_dir_name
    result = finder.find_from_explicit_definition(for_directory=child_dir)

    assert result == expected_path


def test_find_from_explicit_definition_no_parent_search(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we do not search parent directories when or_any_parent is False."""
    parent_dir = temp_dir / "parent"
    child_dir = parent_dir / "child"
    child_dir.mkdir(parents=True)

    env_file_path = parent_dir / ".env"
    docs_dir_name = "parent_docs"
    env_file_path.write_text(f"PAPE_DOCS_DIR={docs_dir_name}\n")

    result = finder.find_from_explicit_definition(
        for_directory=child_dir,
        or_any_parent=False,
    )
    assert result is None


def test_find_from_implicit_definition_in_current_directory(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we find the docs dir when it's implicitly defined in the current directory."""
    docs_dir_path = temp_dir / "pape-docs"
    docs_dir_path.mkdir()

    result = finder.find_from_implicit_definition(for_directory=temp_dir)
    assert result == docs_dir_path


def test_find_from_implicit_definition_in_parent_directory(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we find the docs directory when it's implicitly defined in a parent directory."""
    parent_dir = temp_dir / "parent"
    child_dir = parent_dir / "child"
    child_dir.mkdir(parents=True)

    docs_dir_path = parent_dir / "pape-docs"
    docs_dir_path.mkdir()

    result = finder.find_from_implicit_definition(for_directory=child_dir)
    assert result == docs_dir_path


def test_find_from_implicit_definition_no_definition(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that we return None when no implicit definition is found."""
    result = finder.find_from_implicit_definition(for_directory=temp_dir)
    assert result is None


def test_search_explicit_definition_preferred(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that search prefers explicit definition over implicit definition."""
    # Explicit definition
    env_file_path = temp_dir / ".env"
    explicit_docs_dir_name = "explicit_docs"
    env_file_path.write_text(f"PAPE_DOCS_DIR={explicit_docs_dir_name}\n")

    # Implicit definition (should be ignored)
    implicit_docs_dir_path = temp_dir / "pape-docs"
    implicit_docs_dir_path.mkdir()

    expected_path = temp_dir / explicit_docs_dir_name
    result = finder.search(starting_at_directory=temp_dir)

    assert result == expected_path


def test_search_implicit_definition_if_no_explicit(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that search uses implicit definition if no explicit definition is found."""
    docs_dir_path = temp_dir / "pape-docs"
    docs_dir_path.mkdir()

    result = finder.search(starting_at_directory=temp_dir)
    assert result == docs_dir_path


def test_search_no_definition(temp_dir: Path, finder: PapeDocsDirectoryFinder) -> None:
    """Test that search returns None when no definition (explicit or implicit) is found."""
    result = finder.search(starting_at_directory=temp_dir)
    assert result is None


def test_find_from_explicit_definition_empty_dot_pape_docs(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that an empty .pape-docs file does not yield a definition."""
    dot_pape_docs_path = temp_dir / ".pape-docs"
    dot_pape_docs_path.touch()  # Create an empty file

    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result is None


def test_find_from_explicit_definition_pyproject_toml_no_docs_dir(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that pyproject.toml without docs-dir in tool.pape-docs does not yield a definition."""
    pyproject_path = temp_dir / "pyproject.toml"
    pyproject_path.write_text('[tool."pape-docs"]\nother-setting = "value"\n')

    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result is None


def test_find_from_explicit_definition_pyproject_toml_no_tool_section(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that pyproject.toml without a tool section does not yield a definition."""
    pyproject_path = temp_dir / "pyproject.toml"
    pyproject_path.write_text('[project]\nname = "my-project"\n')

    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result is None


def test_find_from_explicit_definition_pyproject_toml_no_pape_docs_tool_section(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that pyproject.toml without a tool.pape-docs section does not yield a definition."""
    pyproject_path = temp_dir / "pyproject.toml"
    pyproject_path.write_text('[tool.other-tool]\nsetting = "value"\n')

    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result is None


def test_find_from_explicit_definition_env_file_empty_value(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that a .env file with an empty PAPE_DOCS_DIR value does not yield a definition."""
    env_file_path = temp_dir / ".env"
    env_file_path.write_text("PAPE_DOCS_DIR=\n")

    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result is None


def test_find_from_explicit_definition_priority(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that .env has highest priority, then .pape-docs, then pyproject.toml."""
    # Create all three files with different values
    env_file_path = temp_dir / ".env"
    env_file_path.write_text("PAPE_DOCS_DIR=env_docs\n")

    dot_pape_docs_path = temp_dir / ".pape-docs"
    dot_pape_docs_path.write_text("dot_pape_docs\n")

    pyproject_path = temp_dir / "pyproject.toml"
    pyproject_path.write_text('[tool."pape-docs"]\ndocs-dir = "pyproject_docs"\n')

    # Expect .env to be found first
    expected_path = temp_dir / "env_docs"
    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result == expected_path

    # Remove .env, expect .pape-docs
    env_file_path.unlink()
    expected_path = temp_dir / "dot_pape_docs"
    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result == expected_path

    # Remove .pape-docs, expect pyproject.toml
    dot_pape_docs_path.unlink()
    expected_path = temp_dir / "pyproject_docs"
    result = finder.find_from_explicit_definition(for_directory=temp_dir)
    assert result == expected_path


def test_find_from_explicit_definition_stops_at_root(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that the search for explicit definition stops at the system root."""
    # Create a deep directory structure
    current_dir = temp_dir
    for _ in range(5):
        current_dir = current_dir / "sub"
        current_dir.mkdir(exist_ok=True)

    # Ensure no definition exists anywhere in the path up to the root
    result = finder.find_from_explicit_definition(for_directory=current_dir)
    assert result is None


def test_find_from_implicit_definition_stops_at_root(
    temp_dir: Path,
    finder: PapeDocsDirectoryFinder,
) -> None:
    """Test that the search for implicit definition stops at the system root."""
    # Create a deep directory structure
    current_dir = temp_dir
    for _ in range(5):
        current_dir = current_dir / "sub"
        current_dir.mkdir(exist_ok=True)

    # Ensure no definition exists anywhere in the path up to the root
    result = finder.find_from_implicit_definition(for_directory=current_dir)
    assert result is None

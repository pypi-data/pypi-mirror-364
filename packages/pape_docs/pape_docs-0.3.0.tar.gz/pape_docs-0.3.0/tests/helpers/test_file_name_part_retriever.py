import io
from unittest.mock import patch

from src.helpers.file_name_part_retriever import (
    FileNamePartRetriever,
    get_sanitized_file_name_part,
)


def test_file_name_part_retriever_init_with_initial_value() -> None:
    """Test initialization with an initial value."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value="My Test Title",
        baseline_default="Default",
    )
    assert retriever.argument_name == "title"
    assert retriever.current_value == "My Test Title"
    assert retriever.baseline_default == "Default"
    assert retriever.current_sanitized_value == "My Test Title"
    assert not retriever.already_prompted


def test_file_name_part_retriever_init_with_invalid_initial_value() -> None:
    """Test initialization with an initial value containing invalid characters."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value="My/Test:Title?",
        baseline_default="Default",
    )
    assert retriever.current_value == "My/Test:Title?"
    assert retriever.current_sanitized_value == "MyTest:Title?"


def test_file_name_part_retriever_init_no_initial_value() -> None:
    """Test initialization without an initial value."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        baseline_default="Default",
    )
    assert retriever.current_value is None
    assert retriever.current_sanitized_value == ""


def test_get_sanitized_file_name_part_already_sanitized() -> None:
    """Test when initial value is already sanitized."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value="ValidTitle",
        baseline_default="Default",
    )
    assert retriever.get_sanitized_file_name_part() == "ValidTitle"


def test_get_sanitized_file_name_part_needs_sanitization_accept_default() -> None:
    """Test when value needs sanitization and user accepts the sanitized default."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value="Invalid/Title?",
        baseline_default="Default",
    )
    with patch("sys.stdin", io.StringIO("\n")):
        result = retriever.get_sanitized_file_name_part()

    assert result == "InvalidTitle?"


def test_get_sanitized_file_name_part_needs_sanitization_provide_new() -> None:
    """Test when value needs sanitization and user provides a new valid value."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value="Invalid/Title?",
        baseline_default="Default",
    )
    with patch("click.prompt", return_value="NewValidTitle"):
        result = retriever.get_sanitized_file_name_part()

    assert result == "NewValidTitle"


def test_get_sanitized_file_name_part_empty_initial_value_provide_valid() -> None:
    """Test when initial value is empty and user provides a valid value."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value="",
        baseline_default="Default",
    )
    with patch("click.prompt", return_value="ProvidedTitle"):
        result = retriever.get_sanitized_file_name_part()

    assert result == "ProvidedTitle"


def test_get_sanitized_file_name_part_none_initial_value_provide_valid() -> None:
    """Test when initial value is None and user provides a valid value."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value=None,
        baseline_default="Default",
    )
    with patch("click.prompt", return_value="ProvidedTitle"):
        result = retriever.get_sanitized_file_name_part()

    assert result == "ProvidedTitle"


def test_get_sanitized_file_name_part_invalid_at_inv_then_valid_interactive() -> None:
    """Test when user provides all-invalid input at invocation, then valid input interactively."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value="////",
    )
    with patch("sys.stdin", io.StringIO("\nValidInput\n")):  # First empty, then valid
        result = retriever.get_sanitized_file_name_part()

    assert result == "ValidInput"


def test_get_sanitized_file_name_part_invalid_interactively_then_valid_interactively() -> (
    None
):
    """Test when user provides an all-invalid input interactively."""
    retriever = FileNamePartRetriever(
        argument_name="title",
    )
    with patch(
        "sys.stdin", io.StringIO("////\nValidInput\n"),
    ):  # First all-invalid, then valid
        result = retriever.get_sanitized_file_name_part()

    assert result == "ValidInput"


def test_get_sanitized_file_name_part_loop_until_valid() -> None:
    """Test that the prompt loops until a valid input is provided."""
    retriever = FileNamePartRetriever(
        argument_name="title",
        initial_value="Bad/Input",
        baseline_default="Default",
    )
    side_effects = ["Still/Bad", "GoodInput"]
    with patch("click.prompt", side_effect=side_effects) as mock_prompt:
        result = retriever.get_sanitized_file_name_part()

    assert result == "GoodInput"

    assert mock_prompt.call_count == len(side_effects)
    assert (
        "The title provided at invocation (Bad/Input) contained some characters that cannot be "
        "used in a file name. Press enter to accept the sanitized value (BadInput)"
    ) in mock_prompt.call_args_list[0][0][0]
    assert (
        "The provided title contained some characters that cannot be used in a file name. "
        "Press enter to accept the sanitized value (StillBad) "
    ) in mock_prompt.call_args_list[1][0][0]


def test_get_sanitized_file_name_part_convenience_function_valid() -> None:
    """Test convenience function with valid initial value."""
    with patch("click.prompt", return_value=""):  # Should not be called
        result = get_sanitized_file_name_part(
            argument_name="title",
            initial_value="ValidTitle",
            baseline_default="Default",
        )

    assert result == "ValidTitle"


def test_get_sanitized_file_name_part_convenience_function_needs_prompt() -> None:
    """Test convenience function when prompt is needed."""
    with patch("click.prompt", return_value="NewValidTitle"):
        result = get_sanitized_file_name_part(
            argument_name="title",
            initial_value="Invalid/Title?",
            baseline_default="Default",
        )

    assert result == "NewValidTitle"


def test_get_sanitized_file_name_part_convenience_function_empty_initial_value() -> (
    None
):
    """Test convenience function with empty initial value."""
    with patch("click.prompt", return_value="FilledValue"):
        result = get_sanitized_file_name_part(
            argument_name="title",
            initial_value="",
            baseline_default="Default",
        )

    assert result == "FilledValue"


def test_get_sanitized_file_name_part_convenience_function_none_initial_value() -> None:
    """Test convenience function with None initial value."""
    with patch("click.prompt", return_value="FilledValue"):
        result = get_sanitized_file_name_part(
            argument_name="title",
            initial_value=None,
            baseline_default="Default",
        )

    assert result == "FilledValue"

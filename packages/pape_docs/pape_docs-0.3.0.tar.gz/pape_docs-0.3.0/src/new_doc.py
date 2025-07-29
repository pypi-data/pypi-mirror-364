# # # # # # # # # # # # # # # # # # # #
# Pape Docs
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A CLI script for creating a new document from a template."""

import os
from pathlib import Path

import click

from helpers import (
    dir_write_tester,
    docs_dir_guard,
    file_name_part_retriever,
    pape_docs_dir_finder,
    template_loader,
)


@click.group()
def cli() -> None:
    """Invoke a CLI tool for making docs from a template."""


def _get_docs_directory() -> Path | None:
    """Determine the pape-docs directory based on environment, pyproject.toml, or prompt."""
    # 1. Check PAPE_DOCS_DIR environment variable
    env_docs_dir = os.getenv("PAPE_DOCS_DIR")
    if env_docs_dir:
        docs_dir = Path(env_docs_dir)
        click.echo(
            f"✓ Using docs directory from PAPE_DOCS_DIR environment variable: {docs_dir}",
        )
        return docs_dir

    # 2. Find a docs-dir value
    finder = pape_docs_dir_finder.PapeDocsDirectoryFinder()
    docs_dir = finder.search(starting_at_directory=Path.cwd())
    if docs_dir:
        click.echo(
            f"✓ Found a docs-dir path to use: {docs_dir}",
        )
        return docs_dir

    return None


def _process_invocation_arguments(
    short_title_inv_arg: str | None,
    priority_inv_arg: str | None,
    doc_type_inv_arg: str | None,
) -> tuple[str, str, str]:
    """
    Process the invocation arguments.

    ## Returns

    (
        sanitized_short_name,
        sanitized_priority,
        doc_type,
    )
    """
    return (
        file_name_part_retriever.get_sanitized_file_name_part(
            argument_name="short title",
            initial_value=short_title_inv_arg,
        ),
        file_name_part_retriever.get_sanitized_file_name_part(
            argument_name="priority",
            initial_value=priority_inv_arg,
            baseline_default="????",
        ),
        (
            doc_type_inv_arg
            if doc_type_inv_arg is not None
            else click.prompt(
                "Enter the document type (e.g., 'RFC', 'ADR', 'Note')",
                default="",
                show_default=False,
            )
        ),
    )


@cli.command("new")
@click.argument(
    "short_title",
    required=False,
    type=str,
)
@click.option(
    "--priority",
    "priority",
    required=False,
    type=str,
    help="Priority number to use at the start of the file name.",
)
@click.option(
    "--doc-type",
    "doc_type",
    required=False,
    type=str,
    help="Optional document type for the document.",
)
def new_doc_command(
    short_title: str | None,
    priority: str | None,
    doc_type: str | None,
) -> None:
    """
    Interactively create a new file the docs folder based on the specified template.

    The script asks for the following, in order, skipping values already provided in the
    invocation or determined automatically:

    - the location of the docs directory
    - the short title of the doc (required, no default value)
    - the doc type to use (defaults to `None`)
    - the priority number (actually a string) for the document (defaults to `????`)

    The script then creates a file with a name of the form 'priority short-title.md' in
    the docs folder.
    """
    short_title_inv_arg = short_title
    priority_inv_arg = priority
    doc_type_inv_arg = doc_type

    docs_dir = _get_docs_directory()
    if docs_dir is None:
        error_message = (
            "The script detected no PAPE_DOCS_DIR environment variable, "
            "no .env, .pape-docs, nor pyproject.toml with a pape-docs definition in the current "
            "directory nor any of its parents, "
            "and no pape-docs/ directory in the current directory nor any of its parents."
        )
        raise click.ClickException(error_message)

    docs_dir_guard.ensure_docs_directory_exists(docs_dir)
    dir_write_tester.perform_write_test(in_dir=docs_dir)

    sanitized_short_title, sanitized_priority, doc_type = _process_invocation_arguments(
        short_title_inv_arg,
        priority_inv_arg,
        doc_type_inv_arg,
    )

    filename = f"{sanitized_priority} {sanitized_short_title}.md"
    new_doc_path = docs_dir / filename

    if new_doc_path.exists() and not click.confirm(
        f"File '{new_doc_path}' already exists. Overwrite it?",
    ):
        click.echo("Operation cancelled.")
        return

    new_doc_path.write_text(
        template_loader.generate_document_content(doc_type=doc_type),
    )

    click.echo(f"✓ Document created successfully at {new_doc_path}")


def main() -> None:
    """
    Invoke the CLI while requiring a sub-command such as `new`.

    This enables us to do `uvx pape-docs new` instead of `uvx new-doc --from pape-docs`.
    """
    cli()


if __name__ == "__main__":
    main()

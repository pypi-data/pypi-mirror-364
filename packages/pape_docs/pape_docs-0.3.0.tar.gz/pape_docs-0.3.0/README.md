# Pape Docs

Pape Docs is a command-line interface (CLI) tool designed to simplify the creation and management of templated documentation. It provides a straightforward, opinionated system for generating various types of documents (e.g., ADRs, tasks, notes) from predefined templates, ensuring consistency and reducing overhead.

## Features

### Streamlined Document Creation

The core functionality is provided by the `new-doc` script, which allows users to quickly create new Markdown documents based on pre-defined templates.

**Usage:**

```sh
uvx pape-docs new
```

Or, with `pape-docs` installed via `uv` as a tool (see installation instructions below):

```sh
new-doc
```

**Options:**

- `--priority <PRIORITY>`: Optional priority number for the document (e.g., "0100", "????" for unknown).
- `--doc-type <DOC_TYPE>`: Optional document type (e.g., "ADR", "Task", "Notes", "Bug").

### Robust Interactivity (Planned)

The `new-doc` script is designed to support both interactive and non-interactive modes.

- **Interactive Mode (Default):**
    - Prompts for required arguments (like the document title) if not provided via command-line options.
    - Re-prompts for invalid non-empty responses, providing reasonable defaults for empty responses.
- **Non-Interactive Mode (Planned Option):**
    - Will execute without any interactive prompts.
    - Will throw an error if any required arguments (e.g., title) are missing.

### Flexible Docs Directory Location

The script intelligently locates the `pape-docs/` directory where new documents should be placed. The search order is:

1. An environment variable (`PAPE_DOCS_DIR`).
2. A `pyproject.toml` file in the current or parent directories, looking for `[tool.pape-docs]."docs-dir"`.
3. An existing `pape-docs/` directory in the current or parent directories.

If none is found, the script exits before the user wastes time entering other information

### Packaged Template

Pape Docs comes with one pre-defined `doc.md` template. It's bundled with the application and are not user-configurable. This design choice reinforces the opinionated nature of the tool, aiming to prescribe a simple and consistent documentation system.

## Installation

If you want to add `new-doc` (and `pape-docs`) to your `$PATH`, you can install this package as a `uv` tool.

```sh
uv tool install pape-docs
```

`uv` allows updating tools with `uv tool upgrade [tool-name]` or `uv tool upgrade --all`.

## Development

### Setup

1. Clone the repository.
2. Install dependencies using `uv` (or `pip`):

    ```sh
    uv pip install -e .
    uv pip install -e ".[dev]"
    ```

### Linting and Formatting

This project uses `ruff` for linting and formatting.

```sh
ruff check .
ruff format .
```

### Testing

Tests will be written using `pytest`.

```sh
pytest
```

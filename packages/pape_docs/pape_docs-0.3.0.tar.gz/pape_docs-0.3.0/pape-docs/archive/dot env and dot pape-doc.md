# Discover pape-docs directories via `.env` or `.pape-docs`

A **bugfix/feature**, created on **July 14, 2025**, about **locating `pape-docs/` directories by reading `.env` and `.pape-docs` files**

## Status

Accepted, implemented

## Problem

Currently, non-Python projects have to include a `pyproject.toml` to use this tool correctly, and I don't want to force that.

Really, I should consider requiring a more language- and platform-agnostic way of defining `pape-docs` directories, to simplify things and really enforce that this tool isn't just for Python projects.

## Solution

To address the problem of linking to unwanted `docs/` directories and to provide flexibility for non-Python projects, the utility will discover `pape-docs/` directories by looking for `.env` files (specifically the `PAPE_DOCS_DIR` environment variable) or `.pape-docs` files at the root of a project.

- **Using `.env`:** Projects can define the location of their `pape-docs` directory using a `PAPE_DOCS_DIR` environment variable within a `.env` file at the project root. This approach is particularly useful for community projects where you might want to exclude your personal documentation from the project's git history by also adding a `.gitignore` file to the `pape-docs/` directory.
- **Using `.pape-docs`:** Alternatively, a `.pape-docs` file can be placed at the base of the project. The contents of this file would be a relative or absolute path to the `pape-docs` directory for that project. This allows for the documentation directory to be defined in a file that can be independently included or ignored from git history.

The script will search for both `.env` and `.pape-docs` files to maximize discovery flexibility across different project types and personal preferences.

### Use Cases

- **Personal Python project:** For personal Python projects, the `pape-docs/` directory can still be defined in `pyproject.toml` (if `uv` is used) or automatically discovered if no `pyproject.toml` is present and the structure is simple.
- **Personal non-Python project:** For personal non-Python projects, a `.pape-docs` file at the project base can specify the relative path to the `pape-docs/` directory, allowing it to be included in git history.
- **Community project:** For community projects (Python or non-Python), a `.env` file at the project root can define `PAPE_DOCS_DIR` to point to a `pape-docs/` directory, which can then be excluded from git history using a `.gitignore` file within the `pape-docs/` directory.

## Alternatives considered

### Use more `pyproject.toml`s

One alternative considered was to extend the use of `pyproject.toml` files. The idea was that if a `[tool.pape-docs].docs-dir` option was defined in a `pyproject.toml` in any directory, the script would ignore all subdirectories and link only to that specified `docs-dir`.

The upside of this approach was that it would allow for defining a `pape-docs` directory inside of existing project `docs/` folders (e.g., `byos_laravel/docs/pape-docs/`) and using a `.gitignore` file to prevent it from being committed.

However, this alternative was ultimately rejected for several reasons:

- It would require adding a `pyproject.toml` file to the root of non-Python projects solely for defining the `docs-dir` option, which is semantically incorrect and would necessitate adding it to `.gitignore`.
- More fundamentally, it highlighted a problem with the `pape-docs` package itself, suggesting that the fix should be implemented within `pape-docs` to handle non-Python projects more gracefully, rather than forcing `pyproject.toml` onto them.

## Open questions

What should be the discovery order of `.env` files, `.pape-docs` files, `pyproject.toml` files, and `PAPE_DOCS_DIR` environment variables?

What happens if I come across one of those three files, but it doesn't have a pape-docs directory defined? To I keep looking? It seems like I should...

Should I just ignore `pyproject.toml` files altogether and require the user define a `.pape-docs` or `.env` file to use this tool?

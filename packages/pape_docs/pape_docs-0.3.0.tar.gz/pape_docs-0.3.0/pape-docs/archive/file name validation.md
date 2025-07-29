# The script should validate to the level determined by the user

A **feature proposal**, created on **July 19, 2025**

## Status

Accepted, implemented

## Proposal

Let the user use whatever characters they want in their file name, as long as the OS allows those characters in a file name, and those characters don't cause the file to be placed in a different directory (e.g. this is not allowed as a file name: `../../../../../../../../../../../../var/root/ssh`).

Also, any file type value should be acceptable because that gets written to the file, not used in the file path.

## Details

The `FileNamePartRetriever` class in `src/helpers/file_name_part_retriever.py` handles the sanitization of file name components. It uses the `pathvalidate.sanitize_filename` function to ensure that the provided file name parts are compatible with the operating system's file naming conventions.

The implementation includes an interactive workflow:

- If the user provides an invalid or empty file name part at invocation, the script will prompt them to enter a valid one.
- If the provided value contains characters that cannot be used in a file name but can be sanitized into a usable value, the script will present the sanitized version and ask the user to approve it or provide a new value.

There is no robust testing for the length of the file name or the file path.

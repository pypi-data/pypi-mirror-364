# # # # # # # # # # # # # # # # # # # #
# Pape Docs
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A module that provides the `perform_write_test` function."""

import pathlib

import click


def perform_write_test(*, in_dir: pathlib.Path) -> None:
    """
    Attempt to write a temporary document in the specified directory, then delete it.

    Raises a ClickException on failures.
    """
    test_directory = in_dir
    test_file = test_directory / ".pape-docs-write-test.tmp"

    try:
        test_file.write_text("test")
    except FileNotFoundError as file_not_found_error:
        error_message = (
            f"Docs directory '{test_directory}' does not exist or is not accessible. "
            "Please ensure the directory exists and has proper permissions."
        )
        raise click.ClickException(error_message) from file_not_found_error
    except OSError as os_error:
        error_message = (
            f"Cannot write to docs directory '{test_directory}' due to a permission error. "
            "Please check your write permissions for this directory."
        )
        raise click.ClickException(error_message) from os_error
    except Exception as exception:
        error_message = "Error writing to docs directory."
        raise click.ClickException(error_message) from exception

    try:
        test_file.unlink()
    except Exception as exception:
        error_message = (
            f"Error deleting temporary file '{test_file}'. You may need to delete it manually."
        )
        raise click.ClickException(error_message) from exception

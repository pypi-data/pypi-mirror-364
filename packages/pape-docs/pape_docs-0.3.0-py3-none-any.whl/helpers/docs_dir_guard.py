# # # # # # # # # # # # # # # # # # # #
# Pape Docs
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A module that provides the `ensure_docs_directory_exists` function."""

import pathlib

import click


def ensure_docs_directory_exists(docs_dir: pathlib.Path) -> None:
    """Interactively ensure the docs directory exists."""
    if not docs_dir.exists():
        if click.confirm(f"Docs directory '{docs_dir}' does not exist. Create it?"):
            try:
                docs_dir.mkdir(exist_ok=True)
                click.echo(f"✓ Created docs directory: {docs_dir}")
            except PermissionError as permission_error:
                error_message = (
                    f"Could not create '{docs_dir}' because of insufficient permissions."
                )
                raise click.ClickException(error_message) from permission_error
            except FileNotFoundError as file_not_found_error:
                error_message = (
                    f"Could not create '{docs_dir}' because the parent directory "
                    f'does not exist. Fix with `mkdir -p "{docs_dir}"`'
                )
                raise click.ClickException(error_message) from file_not_found_error
            except Exception as exception:
                error_message = f"Error creating docs directory: {exception}"
                raise click.ClickException(error_message) from exception
        else:
            click.echo("Operation cancelled. Docs directory not created.")
            raise click.Abort

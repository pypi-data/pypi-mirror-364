# # # # # # # # # # # # # # # # # # # #
# Pape Docs
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A module that provides the `PapeDocsDirectoryFinder` class."""

import logging
import pathlib
import tomllib

import dotenv

_logger = logging.getLogger(__name__)


class PapeDocsDirectoryFinder:
    """
    A class that facilitates the search for a pape-docs, based on a starting location.

    If there is no explicit or implicit definition, the function returns `None`.
    """

    def find_from_explicit_definition(
        self,
        *,
        for_directory: pathlib.Path,
        or_any_parent: bool = True,
    ) -> pathlib.Path | None:
        """
        Perform a search for an explicit pape-docs definition, starting at the specified directory.

        The search for an explicit definition starts at the `for_directory`, looking in the
        following files (in order, stopping when an explicit definition is found):

        1. `.env`
        2. `.pape-docs`
        3. `pyproject.toml`

        If there is no explicit definition in `for_directory`, and `or_any_parent == True`, then the
        search continues in the parent and (if necessary) goes until hitting the system root.

        Returns `None` if no explicit definition is found.
        """
        self._current_directory = for_directory
        search_parents = or_any_parent

        if search_parents:
            explicit_value = self._explicit_value_from_current_directory()

            while (
                explicit_value is None and self._current_directory != self._current_directory.parent
            ):
                self._current_directory = self._current_directory.parent
                explicit_value = self._explicit_value_from_current_directory()

            return explicit_value

        return self._explicit_value_from_current_directory()

    def find_from_implicit_definition(
        self,
        *,
        for_directory: pathlib.Path,
    ) -> pathlib.Path | None:
        """
        Return the pape-docs directory path from an implicit definition.

        If there is a `pape-docs` directory in the `search_start_dir_path`, that is the value that
        this function returns. Otherwise, the search continues in the parent, and so on until the
        system root.

        If no `pape-docs` directories are found, returns `None`.
        """
        self._current_directory = for_directory
        for directory in [
            self._current_directory,
            *list(self._current_directory.parents),
        ]:
            potential_docs_dir = directory / "pape-docs"
            if potential_docs_dir.is_dir():
                return potential_docs_dir

        return None

    def _explicit_value_from_current_directory(self) -> pathlib.Path | None:
        return (
            self._value_from_dot_env()
            or self._value_from_dot_pape_docs()
            or self._value_from_pyproject_toml()
        )

    def _value_from_dot_env(self) -> pathlib.Path | None:
        dotenv_path = self._current_directory / ".env"
        if not dotenv_path.exists():
            return None

        dotenv_value = dotenv.main.DotEnv(dotenv_path).get("PAPE_DOCS_DIR")
        if dotenv_value:
            return self._current_directory / dotenv_value

        _logger.info(
            "Found %s, but it didn't contain a PAPE_DOCS_DIR value. Skipping.",
            dotenv_path,
        )
        return None

    def _value_from_dot_pape_docs(self) -> pathlib.Path | None:
        dot_pape_docs_path = self._current_directory / ".pape-docs"
        if not dot_pape_docs_path.exists():
            return None

        dot_pape_docs_contents = dot_pape_docs_path.read_text().strip()
        if dot_pape_docs_contents:
            return self._current_directory / dot_pape_docs_contents

        _logger.info(
            "Found %s, but it was empty. Skipping.",
            dot_pape_docs_path,
        )
        return None

    def _value_from_pyproject_toml(self) -> pathlib.Path | None:
        pyproject_path = self._current_directory / "pyproject.toml"
        if not pyproject_path.exists():
            return None

        with pyproject_path.open("r", encoding="utf-8") as f:
            pyproject_content = tomllib.loads(f.read())

        tool_config = pyproject_content.get("tool", {}).get("pape-docs", {})
        if "docs-dir" in tool_config:
            return self._current_directory / tool_config["docs-dir"]

        _logger.info(
            "Found %s, but it didn't contain [tool.pape-docs].docs-dir. Skipping.",
            pyproject_path,
        )
        return None

    def search(
        self,
        *,
        starting_at_directory: pathlib.Path,
    ) -> pathlib.Path | None:
        """
        Search for an explicit definition then, if necessary, an implicit definition.

        If the function finds neither an explicit nor implicit definition, it returns `None`.
        """
        return self.find_from_explicit_definition(
            for_directory=starting_at_directory,
        ) or self.find_from_implicit_definition(
            for_directory=starting_at_directory,
        )

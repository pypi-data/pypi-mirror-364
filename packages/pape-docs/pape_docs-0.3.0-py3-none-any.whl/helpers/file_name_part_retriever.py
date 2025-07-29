# # # # # # # # # # # # # # # # # # # #
# Pape Docs
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A module that provides the `FileNamePartRetriever` class and convenience function."""

import click
import pathvalidate


def get_sanitized_file_name_part(
    *,
    argument_name: str,
    initial_value: str | None = None,
    baseline_default: str | None = None,
    already_prompted: bool = True,
) -> str:
    """Invoke a convenience function for `FileNamePartRetriever.get_sanitized_file_name_part`."""
    return FileNamePartRetriever(
        argument_name=argument_name,
        initial_value=initial_value,
        baseline_default=baseline_default,
        already_prompted=already_prompted,
    ).get_sanitized_file_name_part()


class FileNamePartRetriever:
    """A class for getting any argument that will be part of a file name."""

    def __init__(
        self,
        *,
        argument_name: str,
        initial_value: str | None = None,
        baseline_default: str | None = None,
        already_prompted: bool = False,
    ) -> None:
        """
        Create a retriever.

        ## Parameters
        - `argument_name`: The name of the argument. This is used in interactive prompts.
        - `initial_value`: The value of the argument provided at invocation, if any.
        - `baseline_default`: The default value of the argument if none is provided interactively.
        - `first_prompt`: Whether user has already been prompted for the value interactively.
        """
        self.argument_name = argument_name
        self.current_value = initial_value
        self.baseline_default = baseline_default
        self.already_prompted = already_prompted

        self._sanitize_current_value()

    def _sanitize_current_value(self) -> None:
        self.current_sanitized_value = pathvalidate.sanitize_filename(
            filename=self.current_value if self.current_value else "",
            platform="auto",
        )

    def get_sanitized_file_name_part(self) -> str:
        """Get the specified file name part, doing sanitization and re-prompting as necessary."""
        if self.current_value and self.current_value == self.current_sanitized_value:
            return self.current_sanitized_value

        self._sanitize_current_value()
        while not (self.current_value and self.current_value == self.current_sanitized_value):
            self._prompt_for_value()
            self._sanitize_current_value()

        return self.current_sanitized_value

    def _prompt_for_value(self) -> None:
        if self.current_value is None and not self.already_prompted:
            # The user did not enter an invocation argument,
            # and we are asking them for the first time to provide one.
            self.current_value = click.prompt(
                f"Enter the {self.argument_name} to use in the file name",
                default=self.baseline_default,
            )
        elif self.current_value == "" and not self.already_prompted:
            # The user provided an empty invocation argument,
            # and we are asking them for the first time to provide a new one.
            self.current_value = click.prompt(
                f"The {self.argument_name} provided at invocation was empty. "
                f"Provide a {self.argument_name} to use in the file name",
                default=self.baseline_default,
            )
        elif self.current_sanitized_value == "" and not self.already_prompted:
            # The user provided a non-empty invocation argument,
            # but it only contained invalid characters,
            # and we are asking them for the first time to provide a new one.
            self.current_value = click.prompt(
                f"The {self.argument_name} provided at invocation ({self.current_value}) "
                "only contained characters that cannot be used in a file name. "
                f"Provide a {self.argument_name} to use in the file name",
                default=self.baseline_default,
            )
        elif not self.already_prompted:
            # The user provided a non-empty invocation argument,
            # and it contained invalid characters,
            # but the sanitized value is usable,
            # and we are asking them for the first time to approve the sanitized value.
            self.current_value = click.prompt(
                f"The {self.argument_name} provided at invocation ({self.current_value}) "
                "contained some characters that cannot be used in a file name. "
                f"Press enter to accept the sanitized value ({self.current_sanitized_value}) "
                f"or enter a new one",
                default=self.current_sanitized_value,
                show_default=False,
            )
        elif self.current_sanitized_value == "":
            # The user provided a value interactively,
            # but it only contained invalid characters.
            self.current_value = click.prompt(
                f"The provided {self.argument_name} "
                "only contained characters that cannot be used in a file name. "
                f"Provide a valid {self.argument_name}",
                default=self.baseline_default,
            )
        else:
            # The user provided a value interactively,
            # but it contained invalid characters.
            self.current_value = click.prompt(
                f"The provided {self.argument_name} "
                "contained some characters that cannot be used in a file name. "
                f"Press enter to accept the sanitized value ({self.current_sanitized_value}) "
                f"or enter a new one",
                default=self.current_sanitized_value,
                show_default=False,
            )
        self.already_prompted = True

# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Exceptions raised by the library."""

from typing import TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    from polymatch.base import AnyPattern

__all__ = [
    "PatternCompileError",
    "PatternNotCompiledError",
    "PatternTextTypeMismatchError",
    "DuplicateMatcherRegistrationError",
    "NoSuchMatcherError",
    "NoMatchersAvailableError",
]


class PatternCompileError(ValueError):
    """Error used when a pattern fails to compile."""


class PatternNotCompiledError(ValueError):
    """Error for when a pattern is used without compiling."""


class PatternTextTypeMismatchError(TypeError):
    """Error for when pattern text type doesn't match input text type."""

    def __init__(
        self, pattern_type: "type[AnyPattern]", text_type: type[AnyStr]
    ) -> None:
        """Construct pattern type mismatch error.

        Arguments:
            pattern_type: Pattern matcher type
            text_type: Input text type
        """
        super().__init__(
            f"Pattern of type {pattern_type.__name__!r} can not match text of "
            f"type {text_type.__name__!r}"
        )


class DuplicateMatcherRegistrationError(ValueError):
    """Error for when a duplicate pattern type is registered."""

    def __init__(self, name: str) -> None:
        """Construct duplicate registration error.

        Args:
            name: name of the duplicate matcher
        """
        super().__init__(f"Attempted o register a duplicate matcher {name!r}")


class NoSuchMatcherError(LookupError):
    """Matcher not found."""


class NoMatchersAvailableError(ValueError):
    """No matchers to query against."""

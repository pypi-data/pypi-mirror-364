# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Basic string matchers (exact and contains)."""

from typing import AnyStr

from polymatch import PolymorphicMatcher


class ExactMatcher(PolymorphicMatcher[AnyStr, AnyStr]):
    """Match an entire string."""

    def compile_pattern(self, raw_pattern: AnyStr) -> AnyStr:
        """Compile pattern case-sensitive."""
        return raw_pattern

    def compile_pattern_cs(self, raw_pattern: AnyStr) -> AnyStr:
        """Compile pattern case-sensitive."""
        return raw_pattern

    def compile_pattern_ci(self, raw_pattern: AnyStr) -> AnyStr:
        """Compile pattern case-insensitive."""
        return raw_pattern.lower()

    def compile_pattern_cf(self, raw_pattern: AnyStr) -> AnyStr:
        """Compile pattern case-folded."""
        if isinstance(raw_pattern, str):
            return raw_pattern.casefold()

        msg = "Casefold is not supported on bytes patterns"
        raise TypeError(msg)

    def match_text(self, pattern: AnyStr, text: AnyStr) -> bool:
        """Check that pattern and text are equal."""
        return text == pattern

    @classmethod
    def get_type(cls) -> str:
        """Pattern type."""
        return "exact"


class ContainsMatcher(PolymorphicMatcher[AnyStr, AnyStr]):
    """Match that a pattern exists in a string."""

    def compile_pattern(self, raw_pattern: AnyStr) -> AnyStr:
        """Compile pattern text case-sensitive."""
        return raw_pattern

    def compile_pattern_cs(self, raw_pattern: AnyStr) -> AnyStr:
        """Compile pattern text case-sensitive."""
        return raw_pattern

    def compile_pattern_ci(self, raw_pattern: AnyStr) -> AnyStr:
        """Compile pattern text case-insensitive."""
        return raw_pattern.lower()

    def compile_pattern_cf(self, raw_pattern: AnyStr) -> AnyStr:
        """Compile pattern text case-folded."""
        if isinstance(raw_pattern, bytes):
            msg = "Casefold is not supported on bytes patterns"
            raise TypeError(msg)

        return raw_pattern.casefold()

    def match_text(self, pattern: AnyStr, text: AnyStr) -> bool:
        """Check that pattern exists in text."""
        return pattern in text

    @classmethod
    def get_type(cls) -> str:
        """Pattern type."""
        return "contains"

# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Regex pattern matcher."""

from typing import AnyStr

import regex

from polymatch import PolymorphicMatcher


class RegexMatcher(PolymorphicMatcher[AnyStr, "regex.Pattern[AnyStr]"]):
    """Match string against a regex pattern."""

    def compile_pattern(
        self, raw_pattern: AnyStr, *, flags: int = 0
    ) -> "regex.Pattern[AnyStr]":
        """Compile pattern case-sensitive."""
        return regex.compile(raw_pattern, flags)

    def compile_pattern_cs(
        self, raw_pattern: AnyStr
    ) -> "regex.Pattern[AnyStr]":
        """Compile pattern case-sensitive."""
        return self.compile_pattern(raw_pattern)

    def compile_pattern_ci(
        self, raw_pattern: AnyStr
    ) -> "regex.Pattern[AnyStr]":
        """Compile pattern case-insensitive."""
        return self.compile_pattern(raw_pattern, flags=regex.IGNORECASE)

    def compile_pattern_cf(
        self, raw_pattern: AnyStr
    ) -> "regex.Pattern[AnyStr]":
        """Compile pattern case-folded."""
        return self.compile_pattern(
            raw_pattern, flags=regex.FULLCASE | regex.IGNORECASE
        )

    def match_text(
        self, pattern: "regex.Pattern[AnyStr]", text: AnyStr
    ) -> bool:
        """Match text."""
        return pattern.match(text) is not None

    def match_text_cf(
        self, pattern: "regex.Pattern[AnyStr]", text: AnyStr
    ) -> bool:
        """Match text case-folded."""
        return self.match_text(pattern, text)

    def match_text_ci(
        self, pattern: "regex.Pattern[AnyStr]", text: AnyStr
    ) -> bool:
        """Match text case-insensitive."""
        return self.match_text(pattern, text)

    def match_text_cs(
        self, pattern: "regex.Pattern[AnyStr]", text: AnyStr
    ) -> bool:
        """Match text case-sensitive."""
        return self.match_text(pattern, text)

    @classmethod
    def get_type(cls) -> str:
        """Pattern type."""
        return "regex"

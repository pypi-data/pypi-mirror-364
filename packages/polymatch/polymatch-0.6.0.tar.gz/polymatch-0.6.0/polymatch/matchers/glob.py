# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Glob pattern matcher."""

from fnmatch import translate
from typing import TYPE_CHECKING, AnyStr

from polymatch.matchers.regex import RegexMatcher

if TYPE_CHECKING:
    import regex


class GlobMatcher(RegexMatcher[AnyStr]):
    """Match glob patterns.

    Implemented as a subclass of RegexMatcher, glob patterns are translated to regex on compilation.
    """

    def compile_pattern(
        self, raw_pattern: AnyStr, *, flags: int = 0
    ) -> "regex.Pattern[AnyStr]":
        """Override RegexMatcher compile to transform glob-syntax."""
        if isinstance(raw_pattern, str):
            res = translate(raw_pattern)
        else:
            # Mimic how fnmatch handles bytes patterns
            pat_str = str(raw_pattern, "ISO-8859-1")
            res_str = translate(pat_str)
            res = bytes(res_str, "ISO-8859-1")

        return RegexMatcher.compile_pattern(self, res, flags=flags)

    @classmethod
    def get_type(cls) -> str:
        """Pattern type."""
        return "glob"

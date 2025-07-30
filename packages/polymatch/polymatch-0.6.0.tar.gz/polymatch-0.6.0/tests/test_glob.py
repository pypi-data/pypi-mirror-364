# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Test glob matcher."""

import pytest

from polymatch import pattern_registry

data = (
    ("glob::*", "", True),
    ("glob::*?", "", False),
    ("glob::*?", "a", True),
    ("glob:cf:*!*@thing", "itd!a@thing", True),
    (b"glob:ci:*!*@thing", b"itd!a@thing", True),
    (b"glob:*!*@thing", b"itd!a@thing", True),
    (b"glob:*!*@thing", b"itd!a@THING", False),
)


@pytest.mark.parametrize(("pattern", "text", "result"), data)
def test_patterns(pattern: str, text: str, result: bool) -> None:
    """Ensure various patterns match their expected text."""
    matcher = pattern_registry.pattern_from_string(pattern)
    matcher.compile()
    assert bool(matcher == text) is result


def test_invert() -> None:
    """Ensure parsing inverted pattern works."""
    pattern = pattern_registry.pattern_from_string("~glob::beep")
    pattern.compile()
    assert pattern.inverted

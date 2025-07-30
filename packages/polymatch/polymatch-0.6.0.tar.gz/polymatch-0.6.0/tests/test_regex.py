# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Test regex matcher."""

import pytest

from polymatch import pattern_registry

data = (
    (r"regex::\btest\b", "test", True),
    (r"regex::\btest\b", "test1", False),
    (r"regex::\btest\b", "test response", True),
    (r"regex:cf:\btest\b", "TEST", True),
    (r"regex:cs:foo", "FOO", False),
    (r"regex:cs:foo", "foo", True),
    (r"regex:ci:foo", "FOO", True),
    (r"regex:ci:foo", "foo", True),
)


@pytest.mark.parametrize(("pattern", "text", "result"), data)
def test_patterns(pattern: str, text: str, result: bool) -> None:
    """Test various patterns against different inputs."""
    matcher = pattern_registry.pattern_from_string(pattern)
    matcher.compile()
    assert bool(matcher == text) is result


def test_invert() -> None:
    """Test pattern invert."""
    pattern = pattern_registry.pattern_from_string("~regex::beep")
    pattern.compile()
    assert pattern.inverted

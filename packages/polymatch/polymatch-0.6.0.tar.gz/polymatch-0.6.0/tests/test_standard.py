# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Test standard matchers."""

import pytest

from polymatch import pattern_registry

data = (
    ("exact::a", "a", True),
    ("exact::b", "n", False),
    ("exact::cc", "cc", True),
    ("contains::air", "i", False),
    ("contains::i", "air", True),
    ("exact:a", "a", True),
    ("exact:a", "A", False),
    ("exact:cs:b", "n", False),
    ("exact:cs:cc", "cc", True),
    ("exact:cs:cc", "cc", True),
    ("contains:cs:air", "i", False),
    ("contains:cs:air", "I", False),
    ("contains:cs:i", "air", True),
    ("contains::i", "AIR", False),
    ("contains:ci:i", "AIR", True),
    ("contains:cf:i", "AIR", True),
)


@pytest.mark.parametrize(("pattern", "text", "result"), data)
def test_patterns(pattern: str, text: str, result: bool) -> None:
    """Test expected pattern matches.

    Args:
        pattern: Pattern string to test.
        text: Text to match against.
        result: Whether the text is expected to match.
    """
    matcher = pattern_registry.pattern_from_string(pattern)
    matcher.compile()
    assert bool(matcher == text) is result


def test_invert() -> None:
    """Ensure inverted patterns are parsed correctly."""
    pattern = pattern_registry.pattern_from_string("~exact::beep")
    pattern.compile()
    assert pattern.inverted


def test_repr() -> None:
    """Ensure __repr__() for strings patterns represents the pattern text."""
    pattern = pattern_registry.pattern_from_string("~exact:ci:beep")
    pattern.compile()
    assert (
        repr(pattern)
        == "ExactMatcher(pattern='beep', case_action=CaseAction.CASEINSENSITIVE, invert=True)"
    )


def test_repr_bytes() -> None:
    """Ensure __repr__() for bytes patterns represents the pattern text."""
    pattern = pattern_registry.pattern_from_string(b"~exact:ci:beep")
    pattern.compile()
    assert (
        repr(pattern)
        == "ExactMatcher(pattern=b'beep', case_action=CaseAction.CASEINSENSITIVE, invert=True)"
    )


def test_str() -> None:
    """Ensure that __str__() on string patterns always returns strings."""
    pattern = pattern_registry.pattern_from_string("~exact:ci:beep")
    pattern.compile()
    assert str(pattern) == "~exact:ci:beep"


def test_str_bytes() -> None:
    """Ensure that __str__() on bytes patterns always returns strings."""
    pattern = pattern_registry.pattern_from_string(b"~exact:ci:beep")
    pattern.compile()
    assert str(pattern) == "~exact:ci:beep"


def test_to_string() -> None:
    """Ensure string patterns serialize to strings."""
    pattern = pattern_registry.pattern_from_string("~exact:ci:beep")
    pattern.compile()
    assert pattern.to_string() == "~exact:ci:beep"


def test_to_string_bytes() -> None:
    """Ensure bytes patterns serialize to bytes."""
    pattern = pattern_registry.pattern_from_string(b"~exact:ci:beep")
    pattern.compile()
    assert pattern.to_string() == b"~exact:ci:beep"


def test_cf_match_bytes() -> None:
    """Test exact matcher match_text_cf() handling of bytes objects."""
    matcher = pattern_registry.pattern_from_string("~exact:ci:foo")
    matcher.compile()
    with pytest.raises(TypeError):
        matcher.match_text_cf(b"cc", b"foo")


def test_cf_compile_bytes_bypass() -> None:
    """Test exact matcher compile_pattern_cf() handling of bytes objects."""
    matcher = pattern_registry.pattern_from_string("~exact:cf:foo")
    matcher.compile()
    with pytest.raises(TypeError):
        matcher.compile_pattern_cf(b"foo")


def test_contains_cf_match_bytes() -> None:
    """Test what happens if a bytes object somehow hits match_text_cf()."""
    matcher = pattern_registry.pattern_from_string("contains:cf:foo")
    matcher.compile()
    with pytest.raises(TypeError):
        matcher.match_text_cf(b"cc", b"foo")


def test_contains_cf_compile_bytes_bypass() -> None:
    """Test what happens if a bytes object somehow hits compile_pattern_cf()."""
    matcher = pattern_registry.pattern_from_string("contains:cf:foo")
    matcher.compile()
    with pytest.raises(TypeError):
        matcher.compile_pattern_cf(b"foo")

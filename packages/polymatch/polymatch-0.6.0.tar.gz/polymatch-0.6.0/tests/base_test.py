# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Test base patterns."""

import pytest

from polymatch import pattern_registry
from polymatch.base import CaseAction
from polymatch.error import (
    PatternNotCompiledError,
    PatternTextTypeMismatchError,
)
from polymatch.matchers.standard import ExactMatcher


def test_case_action_validate() -> None:
    """Ensure an informative error is raised when a bytes pattern is configured with casefolding."""
    with pytest.raises(
        TypeError, match="Case-folding is not supported with bytes patterns"
    ):
        _ = ExactMatcher(b"foo", CaseAction.CASEFOLD)


def test_type_mismatch() -> None:
    """Test comparing a bytes pattern against a string."""
    matcher = ExactMatcher(b"foo", CaseAction.CASEINSENSITIVE)
    with pytest.raises(PatternTextTypeMismatchError):
        matcher.match("foo")  # type: ignore[arg-type]


def test_compare() -> None:
    """Test basic comparison."""
    matcher = pattern_registry.pattern_from_string("exact:ci:foo")
    matcher.compile()
    res = matcher == 123
    assert not res
    res = matcher != "aaaaa"
    assert res
    res = matcher != "foo"
    assert not res
    res = matcher != 123
    assert res


def test_compare_invert() -> None:
    """Test inverted compare."""
    matcher = pattern_registry.pattern_from_string("~exact:ci:foo")
    matcher.compile()
    assert matcher == "lekndlwkn"
    assert matcher != "FOO"


def test_compare_no_compile() -> None:
    """Test comparing against an uncompiled pattern."""
    matcher = pattern_registry.pattern_from_string("~exact:ci:foo")
    with pytest.raises(PatternNotCompiledError):
        matcher.match("foo")

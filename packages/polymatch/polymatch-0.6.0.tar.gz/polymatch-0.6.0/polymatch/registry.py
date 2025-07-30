# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Pattern matcher registry.

This also implements parsing the pattern from a simple string e.g.:
    >>> from polymatch.registry import pattern_registry
    >>> pat = pattern_registry.pattern_from_string("contains:ci:foo")
    >>> pat.compile()
    >>> pat == "this is Foo Bar"
    True

"""

from collections import OrderedDict
from typing import Any, AnyStr, Optional

from polymatch.base import CaseAction, PolymorphicMatcher
from polymatch.error import (
    DuplicateMatcherRegistrationError,
    NoMatchersAvailableError,
    NoSuchMatcherError,
)
from polymatch.matchers.glob import GlobMatcher
from polymatch.matchers.regex import RegexMatcher
from polymatch.matchers.standard import ContainsMatcher, ExactMatcher


def _opt_split(
    text: AnyStr, delim: AnyStr, empty: AnyStr, invchar: AnyStr
) -> tuple[bool, AnyStr, AnyStr, AnyStr]:
    if text.startswith(invchar):
        invert = True
        text = text[len(invchar) :]
    else:
        invert = False

    if delim in text:
        name, _, text = text.partition(delim)

        if delim in text:
            opts, _, text = text.partition(delim)
        else:
            opts = empty
    else:
        name = empty
        opts = empty

    return invert, name, opts, text


def _parse_pattern_string(text: AnyStr) -> tuple[bool, str, str, AnyStr]:
    if isinstance(text, str):
        invert, name, opts, pattern = _opt_split(text, ":", "", "~")
        return invert, name, opts, pattern

    if isinstance(text, bytes):
        invert, name, opts, pattern = _opt_split(text, b":", b"", b"~")
        return invert, name.decode(), opts.decode(), pattern

    msg = f"Unable to parse pattern string of type {type(text).__name__!r}"
    raise TypeError(msg)


_Matcher = PolymorphicMatcher[Any, Any]
_MatcherCls = type[_Matcher]


class PatternMatcherRegistry:
    """Registry for pattern types."""

    def __init__(self) -> None:
        """Construct the registry."""
        self._matchers: dict[str, _MatcherCls] = OrderedDict()

    def register(self, cls: type[Any]) -> None:
        """Register a pattern type.

        Args:
            cls: Pattern type to register.

        Raises:
            TypeError: If the pattern is not an implementation of PolymorphicMatcher
            DuplicateMatcherRegistrationError: If a matching pattern is already registered
        """
        if not issubclass(cls, PolymorphicMatcher):
            msg = (
                "Pattern matcher must be of type "
                f"{PolymorphicMatcher.__name__!r} "
                f"not {cls.__name__!r}"
            )
            raise TypeError(msg)

        name = cls.get_type()
        if name in self._matchers:
            raise DuplicateMatcherRegistrationError(name)

        self._matchers[name] = cls

    def remove(self, name: str) -> None:
        """Remove a pattern type from the registry.

        Args:
            name: Pattern type to remove
        """
        del self._matchers[name]

    def get_matcher(self, name: str) -> _MatcherCls:
        """Find the matching Matcher object.

        Args:
            name: name of the pattern type.

        Raises:
            NoSuchMatcherError: When a matching pattern type is not registered.

        Returns:
            The Matcher class for the given pattern type.
        """
        try:
            return self._matchers[name]
        except LookupError as e:
            raise NoSuchMatcherError(name) from e

    def get_default_matcher(self) -> _MatcherCls:
        """Retrieve the default matcher used when a pattern string does not specify one.

        Raises:
            NoMatchersAvailableError: When no matchers are registered so no default can be found

        Returns:
            The default pattern type
        """
        if self._matchers:
            return next(iter(self._matchers.values()))

        raise NoMatchersAvailableError

    def pattern_from_string(self, text: AnyStr) -> _Matcher:
        """Parse pattern string to Matcher object.

        Args:
            text: Pattern string to parse.

        Raises:
            LookupError: If the pattern or case-action can't be found.

        Returns:
            The Matcher object as described by the pattern text.
        """
        invert, name, opts, pattern = _parse_pattern_string(text)
        match_cls = (
            self.get_default_matcher() if not name else self.get_matcher(name)
        )

        case_action: Optional[CaseAction] = None
        for action in CaseAction:
            if action.value[1] == opts:
                case_action = action
                break

        if case_action is None:
            msg = f"Unable to find CaseAction for options: {opts!r}"
            raise LookupError(msg)

        return match_cls(pattern, case_action, invert=invert)

    def __getitem__(self, item: str) -> _MatcherCls:
        """Find the matching Matcher object.

        Args:
            item: name of the pattern type.

        Raises:
            NoSuchMatcherError: When a matching pattern type is not registered.

        Returns:
            The Matcher class for the given pattern type.
        """
        return self.get_matcher(item)


pattern_registry = PatternMatcherRegistry()

pattern_registry.register(ExactMatcher)
pattern_registry.register(ContainsMatcher)
pattern_registry.register(GlobMatcher)
pattern_registry.register(RegexMatcher)

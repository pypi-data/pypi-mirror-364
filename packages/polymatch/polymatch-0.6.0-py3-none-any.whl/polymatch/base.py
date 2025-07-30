# SPDX-FileCopyrightText: 2018-present linuxdaemon <linuxdaemon.irc@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Base matcher classes.

Matchers should implement `PolymorphicMatcher`.
"""

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import AnyStr, Callable, Generic, Optional, TypeVar, cast

import polymatch
from polymatch.error import (
    PatternCompileError,
    PatternNotCompiledError,
    PatternTextTypeMismatchError,
)


class CaseAction(Enum):
    """Pattern case matching action."""

    NONE = "none", ""  # Use whatever the pattern's default is
    CASESENSITIVE = "case-sensitive", "cs"  # Fore case sensitivity
    CASEINSENSITIVE = "case-insensitive", "ci"  # Force case insensitivity
    CASEFOLD = "casefold", "cf"  # Force case-folded comparison


AnyPattern = TypeVar("AnyPattern")

TUPLE_V1 = tuple[AnyStr, CaseAction, bool, AnyPattern, type[AnyStr], object]
TUPLE_V2 = tuple[
    str, AnyStr, CaseAction, bool, Optional[AnyPattern], type[AnyStr], object
]

CompileFunc = Callable[[AnyStr], AnyPattern]
MatchFunc = Callable[[AnyPattern, AnyStr], bool]

FuncTuple = tuple[
    CompileFunc[AnyStr, AnyPattern], MatchFunc[AnyPattern, AnyStr]
]


class PolymorphicMatcher(Generic[AnyStr, AnyPattern], metaclass=ABCMeta):
    """Base Matcher which defines the structure and protocol for polymorphic matchers."""

    _empty = object()

    def _get_case_functions(
        self,
    ) -> tuple[CompileFunc[AnyStr, AnyPattern], MatchFunc[AnyPattern, AnyStr]]:
        suffix = self.case_action.value[1]

        if suffix:
            suffix = f"_{suffix}"

        comp_func = cast(
            CompileFunc[AnyStr, AnyPattern],
            getattr(self, f"compile_pattern{suffix}"),
        )
        match_func = cast(
            MatchFunc[AnyPattern, AnyStr], getattr(self, f"match_text{suffix}")
        )
        return comp_func, match_func

    def __init__(
        self,
        pattern: AnyStr,
        /,
        case_action: CaseAction = CaseAction.NONE,
        *,
        invert: bool = False,
    ) -> None:
        """Construct a pattern object.

        Args:
            pattern: Pattern text to use.
            case_action: Case-sensitivity setting to use, NONE means to use the matcher's default.
                Defaults to CaseAction.NONE.
            invert: Whether the pattern match is inverted. Defaults to False.

        Raises:
            TypeError: If a bytes pattern is provided and casefolding is requested.
        """
        self._raw_pattern: AnyStr = pattern
        self._str_type: type[AnyStr] = type(pattern)
        self._compiled_pattern: Optional[AnyPattern] = None
        self._case_action = case_action
        self._invert = invert

        funcs: FuncTuple[AnyStr, AnyPattern] = self._get_case_functions()
        self._compile_func: CompileFunc[AnyStr, AnyPattern] = funcs[0]
        self._match_func: MatchFunc[AnyPattern, AnyStr] = funcs[1]

        if self._case_action is CaseAction.CASEFOLD and self._str_type is bytes:
            msg = "Case-folding is not supported with bytes patterns"
            raise TypeError(msg)

    def try_compile(self) -> bool:
        """Attempt to compile the pattern.

        Returns:
            True if the pattern compiled successfully, False otherwise
        """
        try:
            self.compile()
        except PatternCompileError:
            return False

        return True

    # TODO(linuxdaemon): #59 deprecate and replace with a non-conflicting name.
    # https://github.com/TotallyNotRobots/poly-match/issues/59
    def compile(self) -> None:
        """Compile the pattern using the implementations compile_{ci,cf,cs} methods.

        Raises:
            PatternCompileError: If an error occurs while compiling the pattern.
        """
        try:
            self._compiled_pattern = self._compile_func(self.pattern)
        except Exception as e:
            msg = f"Failed to compile pattern {self.pattern!r}"
            raise PatternCompileError(msg) from e

    def match(self, text: AnyStr) -> bool:
        """Match text against the configured matcher.

        Args:
            text: Text to match

        Raises:
            PatternTextTypeMismatchError: If the type of `text` doesn't
                match the pattern string type
            PatternNotCompiledError: If the matcher pattern has not yet been compiled

        Returns:
            Whether the pattern matches the input text
        """
        if not isinstance(text, self._str_type):
            raise PatternTextTypeMismatchError(self._str_type, type(text))

        if self._compiled_pattern is None:
            # If it wasn't compiled
            msg = "Pattern must be compiled."
            raise PatternNotCompiledError(msg)

        out = self._match_func(self._compiled_pattern, text)

        if self.inverted:
            return not out

        return out

    def is_compiled(self) -> bool:
        """Whether the pattern is compiled."""
        return self._compiled_pattern is not None

    @abstractmethod
    def compile_pattern(self, raw_pattern: AnyStr) -> AnyPattern:
        """Matchers must override this to compile their pattern with default case-sensitivity."""
        raise NotImplementedError

    @abstractmethod
    def compile_pattern_cs(self, raw_pattern: AnyStr) -> AnyPattern:
        """Matchers must override this to compile their pattern with case-sensitive options."""
        raise NotImplementedError

    @abstractmethod
    def compile_pattern_ci(self, raw_pattern: AnyStr) -> AnyPattern:
        """Matchers must override this to compile their pattern with case-insensitive options."""
        raise NotImplementedError

    @abstractmethod
    def compile_pattern_cf(self, raw_pattern: AnyStr) -> AnyPattern:
        """Matchers must override this to compile their pattern with case-folding options."""
        raise NotImplementedError

    @abstractmethod
    def match_text(self, pattern: AnyPattern, text: AnyStr) -> bool:
        """Matchers must implement this to match their pattern against the text input."""
        raise NotImplementedError

    def match_text_cs(self, pattern: AnyPattern, text: AnyStr) -> bool:
        """Default implementation, passes the input unchanged.

        Args:
            pattern: Pattern to match against
            text: Text input to check

        Returns:
            Whether the pattern matches the text
        """
        return self.match_text(pattern, text)

    def match_text_ci(self, pattern: AnyPattern, text: AnyStr) -> bool:
        """Default implementation, .lower()'s the input text.

        Args:
            pattern: Pattern to match against
            text: Text input to check

        Returns:
            Whether the pattern matches the text
        """
        return self.match_text(pattern, text.lower())

    def match_text_cf(self, pattern: AnyPattern, text: AnyStr) -> bool:
        """Default implementation, case-folds the input text.

        Args:
            pattern: Pattern to match against
            text: Text input to check

        Raises:
            TypeError: If a bytes object is passed for case-folding

        Returns:
            Whether the pattern matches the text
        """
        if isinstance(text, bytes):
            msg = "Casefold is not supported on bytes patterns"
            raise TypeError(msg)

        return self.match_text(pattern, text.casefold())

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        """Get pattern type.

        Implementations must implement this.

        Returns:
            The pattern type name
        """
        raise NotImplementedError

    @property
    def pattern(self) -> AnyStr:
        """Raw, uncompiled pattern text."""
        return self._raw_pattern

    @property
    def case_action(self) -> CaseAction:
        """Configured case-sensitivity setting."""
        return self._case_action

    @property
    def inverted(self) -> bool:
        """Whether the pattern is inverted."""
        return self._invert

    def to_string(self) -> AnyStr:
        """Generate pattern string representation, which can be passed to `pattern_from_string()`.

        Returns:
            The pattern string text
        """
        prefix = "~" if self.inverted else ""
        preamble = f"{prefix}{self.get_type()}:{self.case_action.value[1]}:"
        if isinstance(self.pattern, str):
            return f"{preamble}{self.pattern}"

        return preamble.encode() + self.pattern

    def __eq__(self, other: object) -> bool:
        """Compare against input text.

        Args:
            other: The text to compare against

        Returns:
            Whether the other object matches this pattern
        """
        if isinstance(other, self._str_type):
            return self.match(other)

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compare against input text.

        Args:
            other: The text to compare against

        Returns:
            Whether the other object doesn't match this pattern
        """
        if isinstance(other, self._str_type):
            return not self.match(other)

        return NotImplemented

    def __getstate__(self) -> TUPLE_V2[AnyStr, AnyPattern]:
        """Generate object state for pickling.

        Returns:
            A tuple representing the current object state, used by __setstate__(),\
        """
        return (
            polymatch.__version__,
            self.pattern,
            self.case_action,
            self.inverted,
            self._compiled_pattern,
            self._str_type,
            self._empty,
        )

    def __setstate__(self, state: TUPLE_V2[AnyStr, AnyPattern]) -> None:
        """Configure object based on the `state` tuple.

        This is used when un-pickling the pattern objects.

        Args:
            state: State to set
        """
        (
            version,
            self._raw_pattern,
            self._case_action,
            self._invert,
            _compiled_pattern,
            self._str_type,
            self._empty,
        ) = state
        # This is compatibility code, we can't serialize a pickled object to match this
        if _compiled_pattern is self._empty:  # pragma: no cover
            _compiled_pattern = None

        self._compiled_pattern = _compiled_pattern
        self._compile_func, self._match_func = self._get_case_functions()

        if version != polymatch.__version__ and self.is_compiled():
            self.compile()

    def __repr__(self) -> str:
        """Represent the matcher object in an informative way, useful for debugging.

        Returns:
            The repr for this object
        """
        return (
            f"{type(self).__name__}(pattern={self.pattern!r}, "
            f"case_action={self.case_action}, invert={self.inverted!r})"
        )

    def __str__(self) -> str:
        """Represent the pattern as its pattern string, to be passed to `pattern_from_string()`."""
        res = self.to_string()
        if isinstance(res, str):
            return res

        return res.decode()

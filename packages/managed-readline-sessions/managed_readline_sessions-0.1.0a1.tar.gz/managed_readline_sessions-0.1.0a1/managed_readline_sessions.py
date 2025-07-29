import os.path
import sys

from typing import Callable, Iterable, List, Optional

if 'readline' in sys.modules:
    raise ImportError('readline is already imported; we cannot manage a readline session for you')

import readline as _readline

DEFAULT_COMPLETER = None
DEFAULT_COMPLETER_DELIMS = '\t '
DEFAULT_TAB_BINDING = 'tab: self-insert'

_readline.set_completer(DEFAULT_COMPLETER)
_readline.set_completer_delims(DEFAULT_COMPLETER_DELIMS)
_readline.parse_and_bind(DEFAULT_TAB_BINDING)

# Manually manage getting and setting tab bindings (because readline doesn't support getting tab bindings)
_current_tab_binding = DEFAULT_TAB_BINDING


def _readline_get_tab_binding():
    # type: () -> str
    """Get the current tab key binding configuration.

    Returns:
        str: The current tab binding string (e.g., 'tab: complete')
    """
    global _current_tab_binding

    return _current_tab_binding


def _readline_set_tab_binding(tab_binding):
    # type: (str) -> None
    """Set a new tab key binding configuration.

    Args:
        tab_binding (str): The new tab binding string to configure
    """
    global _current_tab_binding

    _readline.parse_and_bind(tab_binding)
    _current_tab_binding = tab_binding


class _GetTokenCompletionsWrapper:
    """A caching wrapper for token completion functions to improve performance.

    This class memoizes completion results to avoid recomputing them during
    tab completion cycling in readline."""
    __slots__ = (
        '_get_token_completions',
        '_last_incomplete_token_hash',
        '_last_token_completions',
    )

    def __init__(self, get_token_completions):
        # type: (Callable[[str], Iterable[str]]) -> None
        """Initialize a caching wrapper for token completion functions.

        Args:
            get_token_completions: A callable that takes an incomplete token string
                and returns an iterable of possible completions. This will be called
                only when the input token changes to avoid redundant computations.
        """
        self._get_token_completions = get_token_completions  # type: Callable[[str], Iterable[str]]
        self._last_incomplete_token_hash = None  # type: Optional[int]
        self._last_token_completions = []  # type: List[str]

    def __call__(self, incomplete_token, i):
        # type: (str, int) -> Optional[str]
        incomplete_token_hash = hash(incomplete_token)
        if incomplete_token_hash != self._last_incomplete_token_hash:
            self._last_incomplete_token_hash = incomplete_token_hash
            self._last_token_completions = list(self._get_token_completions(incomplete_token))
        if i > len(self._last_token_completions):
            return None
        else:
            return self._last_token_completions[i]


class TabBasedTokenCompletionSession:
    """Context manager for managing readline tab-based token completion sessions.

    Provides safe installation and automatic removal of tab-based token completion functionality."""
    __slots__ = (
        '_completer',
        '_completer_delims',
        '_old_completer',
        '_old_completer_delims',
        '_old_tab_binding',
    )

    def __init__(self, get_token_completions, token_boundary_delimiters=frozenset([' ', '\t'])):
        # type: (Callable[[str], Iterable[str]], Iterable[str]) -> None
        """Initialize a tab-based token completion session manager.

        Args:
            get_token_completions: A callable that takes an incomplete token string
                and returns an iterable of possible completions.
            token_boundary_delimiters: An iterable of single-character delimiters that
                define token boundaries (default: space and tab). All delimiters must
                be single ASCII characters.

        Raises:
            ValueError: If any delimiter is not a single ASCII character.
        """
        self._completer = _GetTokenCompletionsWrapper(get_token_completions)  # type: _GetTokenCompletionsWrapper
        _completer_delim_chars = set()
        for token_boundary_delimiter in token_boundary_delimiters:
            if len(token_boundary_delimiter) == 1 and token_boundary_delimiter.isascii():
                _completer_delim_chars.add(token_boundary_delimiter)
            else:
                raise ValueError('All delimiters must be single ASCII characters.')
        self._completer_delims = ''.join(sorted(_completer_delim_chars)) # type: str

        self._old_completer = _readline.get_completer()
        self._old_completer_delims = _readline.get_completer_delims()
        self._old_tab_binding = _readline_get_tab_binding()

    def __enter__(self):
        """Set up readline completion when entering the context."""
        _readline.set_completer(self._completer)
        _readline.set_completer_delims(self._completer_delims)
        _readline_set_tab_binding('tab: complete')

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Restore previous readline state when exiting the context."""
        _readline.set_completer(self._old_completer)
        _readline.set_completer_delims(self._old_completer_delims)
        _readline_set_tab_binding(self._old_tab_binding)


class ReadWriteHistoryFileSession:
    """Context manager for readline history file operations."""
    __slots__ = (
        '_filename',
    )

    def __init__(self, filename):
        # type: (str) -> None
        """Initialize a history file session manager.

        Args:
            filename: Path to the history file to read from and write to.
                If the file doesn't exist, it will be created when writing.
        """
        self._filename = filename

    def __enter__(self):
        if os.path.isfile(self._filename):
            _readline.read_history_file(self._filename)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _readline.write_history_file(self._filename)
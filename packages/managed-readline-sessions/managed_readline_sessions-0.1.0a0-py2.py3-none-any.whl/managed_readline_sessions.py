import os.path
import sys

from typing import Callable, Iterable, List, Optional

if 'readline' in sys.modules:
    raise ImportError('readline is already imported; we cannot manage a readline session for you')

import readline as _readline

DEFAULT_COMPLETER = None
DEFAULT_COMPLETER_DELIMS = ' \t\n'
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


class GetCompletionsWrapper:
    """A caching wrapper for completion functions to improve performance.

    This class memoizes completion results to avoid recomputing them during
    tab completion cycling in readline.

    Attributes:
        _get_completions: The underlying completion function
        _last_entered_text_hash: Hash of last completion text
        _last_completions: Cached list of completions
    """
    __slots__ = (
        '_get_completions',
        '_last_entered_text_hash',
        '_last_completions',
    )

    def __init__(self, get_completions):
        # type: (Callable[[str], Iterable[str]]) -> None
        self._get_completions = get_completions  # type: Callable[[str], Iterable[str]]
        self._last_entered_text_hash = None  # type: Optional[int]
        self._last_completions = []  # type: List[str]

    def __call__(self, entered_text, i):
        # type: (str, int) -> Optional[str]
        entered_text_hash = hash(entered_text)
        if entered_text_hash != self._last_entered_text_hash:
            self._last_entered_text_hash = entered_text_hash
            self._last_completions = list(self._get_completions(entered_text))
        if i > len(self._last_completions):
            return None
        else:
            return self._last_completions[i]


class CompletionSession:
    """Context manager for managing readline completion sessions.

    Provides safe installation and automatic removal of tab completion
    functionality.

    Attributes:
        completer: The wrapped completion function
        completer_delims: Word boundary delimiters
        old_completer: Previous completer to restore
        old_completer_delims: Previous delimiters to restore
        old_tab_binding: Previous tab binding to restore
    """
    __slots__ = (
        'completer',
        'completer_delims',
        'old_completer',
        'old_completer_delims',
        'old_tab_binding',
    )

    def __init__(self, get_completions, completer_delims=DEFAULT_COMPLETER_DELIMS):
        # type: (Callable[[str], Iterable[str]], str) -> None
        self.completer = GetCompletionsWrapper(get_completions)  # type: GetCompletionsWrapper
        self.completer_delims = completer_delims  # type: str

        self.old_completer = _readline.get_completer()
        self.old_completer_delims = _readline.get_completer_delims()
        self.old_tab_binding = _readline_get_tab_binding()

    def __enter__(self):
        """Set up readline completion when entering the context."""
        _readline.set_completer(self.completer)
        _readline.set_completer_delims(self.completer_delims)
        _readline_set_tab_binding('tab: complete')

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Restore previous readline state when exiting the context."""
        _readline.set_completer(self.old_completer)
        _readline.set_completer_delims(self.old_completer_delims)
        _readline_set_tab_binding(self.old_tab_binding)


class ReadWriteHistoryFileSession:
    """Context manager for readline history file operations.

    Attributes:
        filename: Path to history file
    """
    __slots__ = (
        'filename',
    )

    def __init__(self, filename):
        # type: (str) -> None
        self.filename = filename

    def __enter__(self):
        if os.path.isfile(self.filename):
            _readline.read_history_file(self.filename)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _readline.write_history_file(self.filename)
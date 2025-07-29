# `managed-readline-sessions`

## The Problem

Every Python CLI tool that wants:

- Tab completion
- Command history
- Custom key bindings

...ends up writing the same fragile boilerplate that:

1. Modifies global readline state
2. Often leaks those modifications
3. Reimplements the same completion caching
4. Struggles with nested scenarios

## The Solution

```python
import os.path

from managed_readline_sessions import TabBasedTokenCompletionSession, ReadWriteHistoryFileSession


def token_completer(incomplete_token):
    return [cmd for cmd in ['help', 'exit', 'load'] if cmd.startswith(incomplete_token)]


with ReadWriteHistoryFileSession(os.path.join(os.path.expanduser('~'), '.myapp_history')):
    while True:
        with TabBasedTokenCompletionSession(token_completer):
            try:
                command = input('myapp> ')
                # Process command...
            except EOFError:
                break  # History saved automatically
```

Now your tool has:
- Persistent history
- Tab completion
- Clean state management
- Professional UX

All in just 10 lines of bulletproof code!

## Key Benefits

✓ **Guaranteed cleanup** - Never corrupt a user's shell session again  
✓ **Nested sessions** - Works correctly when called from other tools  
✓ **Performance optimized** - Smart completion caching  
✓ **Battle-tested** - Properly handles edge cases most implementations miss  
✓ **Zero dependencies** - Except `pyreadline` and `typing`, which are pure-Python
✓ **Compatibility** - Supports all operating systems and Python 2+

## Real-World Use Cases

1. **REPLs** - Give users tab completion without breaking their existing shell
2. **CLI tools** - Add history support that persists between runs
3. **Interactive apps** - Implement custom key bindings safely
4. **Debuggers** - Offer completion without interfering with parent process

## Installation

```bash
pip install managed-readline-sessions
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
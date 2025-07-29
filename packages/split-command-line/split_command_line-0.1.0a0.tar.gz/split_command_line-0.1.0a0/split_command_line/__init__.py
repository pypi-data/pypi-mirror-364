import sys

if sys.version_info > (3,):
    unicode = str


class SplitCommandLineNTState:
    NORMAL = 0  # Outside quotes, normal parsing
    IN_QUOTE = 1  # Inside double quotes
    AFTER_BACKSLASH_NORMAL = 2  # After backslash in normal mode
    AFTER_BACKSLASH_IN_QUOTE = 3  # After backslash inside quotes


def split_command_line_nt(command_line_chars):
    """Split a command-line to arguments on NT using explicit state machine.
    Mimics MSVCRT's GetCommandLine.

    The parser follows these rules:
    - Arguments are separated by whitespace
    - Double quotes are used for quoting
    - Backslashes have special meaning only when preceding a quote
    - Environment variables (like %USERNAME%) are not expanded
    - Special characters like *, &, |, >, < are treated literally
    - Adjacent quoted/unquoted segments without whitespace are concatenated into a single argument

    Args:
        command_line_chars: Input string as iterable of characters

    Yields:
        Parsed arguments one by one"""
    char_iter = iter(command_line_chars)
    end_sentinel = object()

    state = SplitCommandLineNTState.NORMAL
    current_token_buffer = []
    backslash_count = 0

    while True:
        char_or_end_sentinel = next(char_iter, end_sentinel)
        if char_or_end_sentinel is end_sentinel:
            break

        char = char_or_end_sentinel  # type: unicode

        # Outside quotes - whitespace separates arguments
        if state == SplitCommandLineNTState.NORMAL:
            if char == u'"':
                state = SplitCommandLineNTState.IN_QUOTE
                continue
            elif char.isspace():
                # Flush current token buffer if not empty
                if current_token_buffer:
                    current_token = u''.join(current_token_buffer)
                    yield current_token
                    current_token_buffer = []
                continue
            elif char == u'\\':
                backslash_count = 1
                state = SplitCommandLineNTState.AFTER_BACKSLASH_NORMAL
                continue
            else:
                current_token_buffer.append(char)
                continue
        # Inside quoted section - most characters are literal
        elif state == SplitCommandLineNTState.IN_QUOTE:
            if char == u'"':
                state = SplitCommandLineNTState.NORMAL
                continue
            elif char == u'\\':
                backslash_count = 1
                state = SplitCommandLineNTState.AFTER_BACKSLASH_IN_QUOTE
                continue
            else:
                current_token_buffer.append(char)
                continue
        # After backslash in normal mode - tracking backslash count
        elif state == SplitCommandLineNTState.AFTER_BACKSLASH_NORMAL:
            if char == u'\\':
                backslash_count += 1
                continue
            elif char == u'"':
                n_paired_quotes, extra_quote = divmod(backslash_count, 2)

                backslash_count = 0

                for _ in range(n_paired_quotes):
                    current_token_buffer.append(u'\\')

                if extra_quote:
                    current_token_buffer.append(u'"')
                    state = SplitCommandLineNTState.NORMAL
                else:
                    state = SplitCommandLineNTState.IN_QUOTE

                continue
            # Non-quote after backslashes - add all as literals
            else:
                for _ in range(backslash_count):
                    current_token_buffer.append(u'\\')
                current_token_buffer.append(char)

                backslash_count = 0
                state = SplitCommandLineNTState.NORMAL

                continue
        elif state == SplitCommandLineNTState.AFTER_BACKSLASH_IN_QUOTE:
            if char == u'\\':
                backslash_count += 1
                continue
            elif char == u'"':
                n_paired_quotes, extra_quote = divmod(backslash_count, 2)

                backslash_count = 0

                for _ in range(n_paired_quotes):
                    current_token_buffer.append(u'\\')

                if extra_quote:
                    current_token_buffer.append(u'"')
                    state = SplitCommandLineNTState.IN_QUOTE
                else:
                    state = SplitCommandLineNTState.NORMAL

                continue
            else:
                for _ in range(backslash_count):
                    current_token_buffer.append(u'\\')
                current_token_buffer.append(char)

                backslash_count = 0
                state = SplitCommandLineNTState.IN_QUOTE

                continue

    # Handle any trailing backslashes not followed by a character
    for _ in range(backslash_count):
        current_token_buffer.append(u'\\')

    # Yield the final token if non-empty
    if current_token_buffer:
        current_token = u''.join(current_token_buffer)
        yield current_token


class SplitCommandLinePosixState:
    NORMAL = 0  # Normal state (not inside quotes)
    IN_SINGLE_QUOTE = 1  # Inside single quotes (no escape parsing)
    IN_DOUBLE_QUOTE = 2  # Inside double quotes (escape sequences parsed)
    ESCAPE_NORMAL = 3  # Next character is escaped, in normal state
    POTENTIAL_ESCAPE_IN_DOUBLE_QUOTE = 4  # Next character might need escaping, in double-quote state


CHARACTERS_TO_ESCAPE_IN_DOUBLE_QUOTE_POSIX = {u'"', u'\\', u'$', u'`'}


def split_command_line_posix(command_line_chars):
    r"""Split a command-line to arguments on POSIX using explicit state machine.
    Behavior closely matches basic POSIX shell parsing but deliberately omits many shell features for safety.

    The parser avoids unsafe shell behaviors:
    - Wildcards, tilde expansion, I/O redirection, joining, piping, variable/command substitution,
      background execution, subshells, control structures, and comments are not handled.

    Quoting and escaping:
        - Outside of quotes:
            - Matches standard POSIX rules.
            - Backslashes escape only the next character, and sequences like \n are not interpreted specially.
        - Strong quotes ('string'):
            - Matches standard POSIX rules.
            - Everything inside is taken literally. Backslashes have no special meaning.
        - Weak quotes ("string"):
            - Matches standard POSIX rules except $ and backticks are not interpreted at all.
            - Supports escaping:
                - \" - literal "
                - \\ - literal \
                - \$ - literal $ (escaping optional, $ has no special meaning)
                - \` - literal backtick (backticks not processed)
            - Sequences like \n are not interpreted specially.
        - Adjacent quoted/unquoted segments without whitespace are concatenated into a single argument.
            - Matches standard POSIX rules.

    Args:
        command_line_chars: Input string as iterable of characters

    Yields:
        Parsed arguments one by one

    Raises:
        ValueError for unclosed quotes and unfinished escapes"""
    char_iter = iter(command_line_chars)
    end_sentinel = object()

    state = SplitCommandLinePosixState.NORMAL
    current_token_buffer = []

    while True:
        char_or_end_sentinel = next(char_iter, end_sentinel)
        if char_or_end_sentinel is end_sentinel:
            break

        char = char_or_end_sentinel  # type: unicode

        if state == SplitCommandLinePosixState.NORMAL:
            if char == u"'":
                state = SplitCommandLinePosixState.IN_SINGLE_QUOTE
                continue
            elif char == u'"':
                state = SplitCommandLinePosixState.IN_DOUBLE_QUOTE
                continue
            elif char.isspace():  # type: ignore
                if current_token_buffer:
                    current_token = u''.join(current_token_buffer)
                    yield current_token
                    current_token_buffer = []
                continue
            elif char == u'\\':
                state = SplitCommandLinePosixState.ESCAPE_NORMAL
                continue
            else:
                current_token_buffer.append(char)
                continue
        elif state == SplitCommandLinePosixState.IN_SINGLE_QUOTE:
            if char == u"'":
                state = SplitCommandLinePosixState.NORMAL
            else:
                current_token_buffer.append(char)
            continue
        elif state == SplitCommandLinePosixState.IN_DOUBLE_QUOTE:
            if char == u'"':
                state = SplitCommandLinePosixState.NORMAL
            elif char == u'\\':
                state = SplitCommandLinePosixState.POTENTIAL_ESCAPE_IN_DOUBLE_QUOTE
            else:
                current_token_buffer.append(char)
            continue
        elif state == SplitCommandLinePosixState.ESCAPE_NORMAL:
            current_token_buffer.append(char)
            state = SplitCommandLinePosixState.NORMAL
            continue
        elif state == SplitCommandLinePosixState.POTENTIAL_ESCAPE_IN_DOUBLE_QUOTE:
            if char in CHARACTERS_TO_ESCAPE_IN_DOUBLE_QUOTE_POSIX:
                current_token_buffer.append(char)
            else:
                current_token_buffer.append(u'\\')
                current_token_buffer.append(char)

            state = SplitCommandLinePosixState.IN_DOUBLE_QUOTE
            continue

    if state != SplitCommandLinePosixState.NORMAL:
        raise ValueError("Unclosed quote/unfinished escape in input")

    # Yield the last token
    if current_token_buffer:
        current_token = u''.join(current_token_buffer)
        yield current_token

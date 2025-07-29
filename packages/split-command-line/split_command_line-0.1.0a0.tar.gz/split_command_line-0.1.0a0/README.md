# split-command-line

A Python library for splitting command-line arguments according to NT (Windows) and POSIX (Unix) rules. Like `shlex.split` but with NT support and without shell features.

## Features

- **Two implementations**:
  - `split_command_line_nt()` for NT-style parsing. Mimics MSVCRT's GetCommandLine.
  - `split_command_line_posix()` for POSIX-style parsing. Behavior closely matches basic POSIX shell parsing but deliberately omits many shell features for safety.
- **No shell features** (wildcards, expansion, substitution, etc.) - pure parsing only
- **Readable, state machine-based** implementations
- **Python 2 and 3** compatible - works with `unicode` on both

## Installation

```bash
pip install split-command-line
```

## Basic Usage

```python
from split_command_line import split_command_line_nt, split_command_line_posix

command_line = u'...'
arguments = list(split_command_line_nt(command_line)) # or list(split_command_line_posix(command_line))
```

## Usage Examples

We can directly execute this module to see how it splits command-line arguments:

```bash
python -m split_command_line nt # or python -m split_command_line posix
```

### NT (Windows) Examples

```
$ python -m split_command_line nt
Enter a command line: %USERNAME%
argv[0]=%USERNAME%

Enter a command line: '%USERNAME%'
argv[0]='%USERNAME%'

Enter a command line: print_argv Hello & print_argv injected
argv[0]=print_argv
argv[1]=Hello
argv[2]=&
argv[3]=print_argv
argv[4]=injected

Enter a command line: print_argv *.txt
argv[0]=print_argv
argv[1]=*.txt

Enter a command line: C:\Users
argv[0]=C:\Users

Enter a command line: C:\Users\
argv[0]=C:\Users\

Enter a command line: C:\Program Files
argv[0]=C:\Program
argv[1]=Files

Enter a command line: "C:\Program Files"
argv[0]=C:\Program Files

Enter a command line: \
argv[0]=\

Enter a command line: \\
argv[0]=\\

Enter a command line: \\\
argv[0]=\\\

Enter a command line: \"
argv[0]="

Enter a command line: \\\"
argv[0]=\"

Enter a command line: \\\\\"
argv[0]=\\"

Enter a command line: "\"\\\""
argv[0]="\"

Enter a command line: "\\\\\"\""
argv[0]=\\""

Enter a command line: "\"abc\" & \"def\""
argv[0]="abc" & "def"

Enter a command line: "\"a&\"b\"c\"d\"\""
argv[0]="a&"b"c"d""
```

### POSIX (Unix) Examples

```
$ python -m split_command_line posix
Enter a command line: ${variable}
argv[0]=${variable}

Enter a command line: $(command)
argv[0]=$(command)

Enter a command line: abc && rm -rf
argv[0]=abc
argv[1]=&&
argv[2]=rm
argv[3]=-rf

Enter a command line: 'a' "b" c
argv[0]=a
argv[1]=b
argv[2]=c

Enter a command line: 'a'"b"c
argv[0]=abc

Enter a command line: 'a'\b"c"
argv[0]=abc

Enter a command line: foo\ bar
argv[0]=foo bar

Enter a command line: 'a\\b'
argv[0]=a\\b

Enter a command line: 'a\"b'
argv[0]=a\"b

Enter a command line: "a\\b"
argv[0]=a\b

Enter a command line: "a\"b"
argv[0]=a"b

Enter a command line: "a"b"
Unclosed quote/unfinished escape in input

Enter a command line: "a$b"
argv[0]=a$b

Enter a command line: "a\$b"
argv[0]=a$b

Enter a command line: "a`b`c"
argv[0]=a`b`c

Enter a command line: "a\`b\`c"
argv[0]=a`b`c

Enter a command line: 'abc
Unclosed quote/unfinished escape in input

Enter a command line: "abc
Unclosed quote/unfinished escape in input

Enter a command line: abc'
Unclosed quote/unfinished escape in input

Enter a command line: abc"
Unclosed quote/unfinished escape in input

Enter a command line: abc\
Unclosed quote/unfinished escape in input
```

## Differences Between Implementations

| Feature                | NT (Windows) | POSIX (Unix) |
|------------------------|--------------|--------------|
| Quote characters       | `"` only     | `'` and `"`  |
| Backslash escaping     | Only before quotes | All characters |
| Special characters     | Treated literally | Some special handling |
| Error handling         | Silent       | Raises ValueError |

## Development

Contributions welcome! Please open issues or pull requests on GitHub.

## License

MIT
from __future__ import print_function
import argparse
import sys

try:
    import readline
except ImportError:
    pass

from . import split_command_line_nt, split_command_line_posix

if sys.version_info < (3,):
    def raw_unicode_input(prompt):
        return raw_input(prompt).decode(sys.stdin.encoding)
else:
    raw_unicode_input = input

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'system',
        choices=['nt', 'posix'],
        help="System type, must be either 'nt' or 'posix'"
    )

    args = parser.parse_args()

    if args.system == 'nt':
        split_command_line_function = split_command_line_nt
    else:
        split_command_line_function = split_command_line_posix

    while True:
        try:
            command_line = raw_unicode_input('Enter a command line: ')
            arguments = list(split_command_line_function(command_line))
            for i, arg in enumerate(arguments):
                print(u'argv[%d]=%s' % (i, arg))
        except ValueError as e:
            print(e, file=sys.stderr)
        except EOFError:
            break
        finally:
            print()
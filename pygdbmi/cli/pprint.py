# The MIT License (MIT)
#
# Copyright (c) 2015 Simon Marchi <simon.marchi@polymtl.ca>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import argparse
from pygdbmi import parser
from pygdbmi import visitors


def main():
    argparser = argparse.ArgumentParser(description='Pretty-print some GDB MI records')
    argparser.add_argument('input_file',
                           metavar='input-file',
                           type=str,
                           help='The file from which to read the MI data. Use - for stdin.')
    argparser.add_argument('-c', '--colors', action='store_true',
                           help='Enable colored output, if possible')

    args = argparser.parse_args()
    input_file = args.input_file

    if input_file == '-':
        f = sys.stdin

    else:
        try:
            f = open(input_file)
        except FileNotFoundError as e:
            print('Error: file not found: {}'.format(e), file=sys.stderr)
            sys.exit(1)

    for line in f:
        if line[-1] != '\n':
            line += '\n'

        try:
            ast = parser.parse(line)
        except parser.ParseError as e:
            print('Error: parse error: {}'.format(e),
                  file=sys.stderr)
            sys.exit(1)

        visitor = visitors.PrettyPrintVisitor(en_colors=args.colors)
        visitor.visit(ast)

    if input_file != '-':
        f.close()


if __name__ == '__main__':
    main()

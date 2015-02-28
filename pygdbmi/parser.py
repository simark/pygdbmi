# The MIT License (MIT)
#
# Copyright (c) 2015 Philippe Proulx <eeppeliteloop@gmail.com>
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

import re
import pypeg2
import pygdbmi.objects


class CString:
    grammar = re.compile(r'"(\\.|[^"])*"')

    def __init__(self, string):
        string = string[1:-1]
        string = bytes(string, 'utf-8').decode('unicode_escape')
        self.value = string

    def __str__(self):
        return '<c-string>{}</c-string>'.format(self.value)


class Variable:
    grammar = re.compile(r'^[A-Za-z_-][A-Za-z_0-9-]*')

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<variable>{}</variable>'.format(self.value)


class Result:
    def __init__(self, args):
        self.variable = args[0]
        self.value = args[1]

    def __str__(self):
        return '<result>{}{}</result>'.format(self.variable, self.value)


class Tuple:
    grammar = '{', pypeg2.optional(pypeg2.csl(Result)), '}'

    def __init__(self, elements=[]):
        if type(elements) is list:
            self.elements = elements
        else:
            self.elements = [elements]

    def __str__(self):
        ret = '<tuple>'

        for elem in self.elements:
            ret += str(elem)

        ret += '</tuple>'

        return ret


class Value:
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return '<value>{}</value>'.format(self.value)


class List:
    grammar = '[', pypeg2.optional([pypeg2.csl(Value), pypeg2.csl(Result)]), ']'

    def __init__(self, elements=[]):
        if type(elements) is list:
            self.elements = elements
        else:
            self.elements = [elements]

    def __str__(self):
        ret = '<list>'

        for elem in self.elements:
            ret += str(elem)

        ret += '</list>'

        return ret


Value.grammar = [CString, Tuple, List]
Result.grammar = Variable, '=', Value


class Token:
    '''
    The token is the optional identifier used to match commands and responses.
    '''
    grammar = re.compile(r'[0-9]+')

    def __init__(self, value):
        self.value = int(value)

    def __str__(self):
        return '<token>{}</token>'.format(self.value)


class ResultRecord:
    grammar = (
        pypeg2.optional(Token),
        '^',
        re.compile(r'done|running|connected|error|exit'),
        pypeg2.optional(','),
        pypeg2.optional(pypeg2.csl(Result)),
        '\n'
    )

    def __init__(self, args):
        self.token = None

        if type(args[0]) is Token:
            self.token = args[0]
            args.pop(0)

        self.result_class = args[0]
        args.pop(0)

        self.results = []

        if args:
            if type(args[0]) is list:
                self.results = args
            else:
                self.results = args

    def __str__(self):
        fmt = '<result-record><token>{}</token><result-class>{}</result-class><results>{}</results></result-record>'
        results = ''

        for result in self.results:
            results += str(result)

        return fmt.format(self.token, self.result_class, results)


class ParseError(RuntimeError):
    pass


def parse(text):
    try:
        return pypeg2.parse(text, ResultRecord,
                                  whitespace=re.compile(r'(?m)(?:\t| )+'))
    except (SyntaxError, Exception) as e:
        raise ParseError(str(e))

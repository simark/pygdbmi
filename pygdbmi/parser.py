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


class _CString:
    grammar = re.compile(r'"(\\.|[^"])*"')

    def __init__(self, string):
        string = string[1:-1]
        string = bytes(string, 'utf-8').decode('unicode_escape')
        self.value = string

    def __str__(self):
        return '<c-string>{}</c-string>'.format(self.value)


class _Variable:
    grammar = re.compile(r'^[A-Za-z_-][A-Za-z_0-9-]*')

    def __init__(self, name):
        self.value = name

    def __str__(self):
        return '<variable>{}</variable>'.format(self.value)


class _Result:
    def __init__(self, args):
        self.variable = args[0]
        self.value = args[1]

    def __str__(self):
        return '<result>{}{}</result>'.format(self.variable, self.value)


class _Tuple:
    grammar = '{', pypeg2.optional(pypeg2.csl(_Result)), '}'

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


class _Value:
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return '<value>{}</value>'.format(self.value)


class _List:
    grammar = '[', pypeg2.optional([pypeg2.csl(_Value), pypeg2.csl(_Result)]), ']'

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


_Value.grammar = [_CString, _Tuple, _List]
_Result.grammar = _Variable, '=', _Value


class _Token:
    grammar = re.compile(r'[0-9]+')

    def __init__(self, value):
        self.value = int(value)

    def __str__(self):
        return '<token>{}</token>'.format(self.value)


class _ResultRecord:
    grammar = (
        pypeg2.optional(_Token),
        '^',
        re.compile(r'done|running|connected|error|exit'),
        pypeg2.optional(','),
        pypeg2.optional(pypeg2.csl(_Result)),
        '\n'
    )

    def __init__(self, args):
        self.token = None

        if type(args[0]) is _Token:
            self.token = args[0]
            args.pop(0)

        self.result_class = args[0]
        args.pop(0)

        self.results = []

        if args:
            if type(args[0]) is list:
                self.results = args[0]
            else:
                self.results = [args[0]]

    def __str__(self):
        fmt = '<result-record><token>{}</token><result-class>{}</result-class><results>{}</results></result-record>'
        results = ''

        for result in self.results:
            results += str(result)

        return fmt.format(self.token, self.result_class, results)


class _GenerateObjectsVisitor:
    def visit(self, rr_node):
        res_class = rr_node.result_class

        if res_class == 'done' or res_class == 'running':
            rr = pygdbmi.objects.DoneResultRecord(rr_node.token,
                                                  rr_node.results)
        elif res_class == 'connected':
            rr = pygdbmi.objects.ConnectedResultRecord(rr_node.token)
        elif res_class == 'error':
            msg = None
            code = None

            for result in rr_node.results:
                if result.variable.value == 'msg':
                    msg = result.value
                elif result.variable.value == 'code':
                    code = result.value

            rr = pygdbmi.objects.ErrorResultRecord(rr_node.token, msg, code)
        elif res_class == 'exit':
            rr = pygdbmi.objects.ExitResultRecord(rr_node.token)

        return rr


class ParseError(RuntimeError):
    pass


class OutputParser:
    def get_parse_tree(self, mitext):
        try:
            parse_tree = pypeg2.parse(mitext, _ResultRecord,
                                      whitespace=re.compile(r'(?m)(?:\t| )+'))
        except (SyntaxError, Exception) as e:
            raise ParseError(str(e))

        return parse_tree

    def parse(self, mitext):
        parse_tree = self.get_parse_tree(mitext)
        visitor = _GenerateObjectsVisitor()

        return visitor.visit(parse_tree)

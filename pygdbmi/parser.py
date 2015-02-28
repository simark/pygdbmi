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
        self.value = string[1:-1]

    def __str__(self):
        v = self.value.replace('&', '&amp;')
        v = v.replace('<', '&lt;')
        v = v.replace('>', '&gt;')
        v = v.replace('"', '&quot;')
        return '<c-string>{}</c-string>'.format(v)


class Variable:
    grammar = re.compile(r'^[A-Za-z_-][A-Za-z_0-9-]*')

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<variable>{}</variable>'.format(self.name)


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


_Nl = pypeg2.ignore(re.compile(r'\r\n|\r|\n'))


class ResultRecord:
    grammar = (
        pypeg2.optional(Token),
        '^',
        re.compile(r'done|running|connected|error|exit'),
        pypeg2.optional((',', pypeg2.csl(Result))),
        _Nl
    )

    def __init__(self, args):
        self.token = None

        if type(args[0]) is Token:
            self.token = args[0]
            args.pop(0)

        self.result_class = args[0]
        args.pop(0)
        self.results = args

    def __str__(self):
        fmt = '<result-record><token>{}</token><result-class>{}</result-class><results>{}</results></result-record>'
        results = ''

        for result in self.results:
            results += str(result)

        return fmt.format(self.token, self.result_class, results)


class _StreamOutput:
    def __init__(self, cstr):
        self.output = cstr

    def __str__(self):
        fmt = '<{xn}>{output}</{xn}>'

        return fmt.format(xn=self._xml_name, output=self.output)

class ConsoleStreamOutput(_StreamOutput):
    grammar = '~', CString, _Nl
    _xml_name = 'console-stream-output'


class TargetStreamOutput(_StreamOutput):
    grammar = '@', CString, _Nl
    _xml_name = 'target-stream-output'


class LogStreamOutput(_StreamOutput):
    grammar = '&', CString, _Nl
    _xml_name = 'log-stream-output'


class StreamRecord:
    grammar = [ConsoleStreamOutput, TargetStreamOutput, LogStreamOutput]

    def __init__(self, output):
        self.output = output

    def __str__(self):
        fmt = '<stream-record>{}</stream-record>'

        return fmt.format(self.output)


_AsyncClass = re.compile(r'[a-zA-Z][a-zA-Z0-9_-]+')


class AsyncOutput:
    grammar = _AsyncClass, pypeg2.optional((',', pypeg2.csl(Result)))

    def __init__(self, args):
        self.async_class = args[0]
        args.pop(0)
        self.results = args

    def __str__(self):
        fmt = '<async-output><async-class>{}</async-class><results>{}</results></async-output>'
        results = ''

        for result in self.results:
            results += str(result)

        return fmt.format(self.async_class, results)


class _AsyncOutput:
    def __init__(self, args):
        self.token = None

        if type(args[0]) is Token:
            self.token = args[0]
            args.pop(0)

        self.output = args[0]

    def __str__(self):
        fmt = '<{xn}><token>{token}</token>{output}</{xn}>'

        return fmt.format(xn=self._xml_name, token=self.token,
                          output=self.output)


class NotifyAsyncOutput(_AsyncOutput):
    grammar = pypeg2.optional(Token), '=', AsyncOutput, _Nl
    _xml_name = 'notify-async-output'


class StatusAsyncOutput(_AsyncOutput):
    grammar = pypeg2.optional(Token), '+', AsyncOutput, _Nl
    _xml_name = 'status-async-output'


class ExecAsyncOutput(_AsyncOutput):
    grammar = pypeg2.optional(Token), '*', AsyncOutput, _Nl
    _xml_name = 'exec-async-output'


class AsyncRecord:
    grammar = [NotifyAsyncOutput, StatusAsyncOutput, ExecAsyncOutput]

    def __init__(self, output):
        self.output = output

    def __str__(self):
        fmt = '<async-record>{}</async-record>'

        return fmt.format(self.output)


class OutOfBandRecord:
    grammar = [AsyncRecord, StreamRecord]

    def __init__(self, record):
        self.record = record

    def __str__(self):
        fmt = '<out-of-band-record>{}</out-of-band-record>'

        return fmt.format(self.record)


class Output:
    grammar = (
        pypeg2.maybe_some(OutOfBandRecord),
        pypeg2.optional(ResultRecord),
        '(gdb)',
        _Nl
    )

    def __init__(self, args):
        self.oob_records = []
        self.result_record = None

        for arg in args:
            if type(arg) is OutOfBandRecord:
                self.oob_records.append(arg)
            elif type(arg) is ResultRecord:
                self.result_record = arg

    def __str__(self):
        fmt = '<output><out-of-band-records>{}</out-of-band-records>{}</output>'
        oob_records = ''

        for oob_record in self.oob_records:
            oob_records += str(oob_record)

        result_record = ''

        if self.result_record is not None:
            result_record = str(self.result_record)

        return fmt.format(oob_records, result_record)


class ParseError(RuntimeError):
    pass


def parse(mi_text, strict=True):
    if not strict:
        if not mi_text.endswith('(gdb)\n'):
            mi_text += '(gdb)\n'

    try:
        return pypeg2.parse(mi_text, Output,
                            whitespace=re.compile(r'(?m)(?:\t| )+'))
    except (SyntaxError, Exception) as e:
        raise ParseError(str(e))

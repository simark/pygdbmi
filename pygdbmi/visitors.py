# The MIT License (MIT)
#
# Copyright (c) 2015 Philippe Proulx <eeppeliteloop@gmail.com>
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
from pygdbmi import parser

try:
    from termcolor import colored
except ImportError:
    def colored(s, c, attrs=[]):
        return s

''' TODO: convert to extend BaseVisitor
class GenerateObjectsVisitor:
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
'''

class BaseVisitor:
    def __init__(self):
        self._visit_fns = {
            parser.ResultRecord: self.visit_result_record,
            parser.Result: self.visit_result,
            parser.Value: self.visit_value,
            parser.CString: self.visit_cstring,
            parser.List: self.visit_list,
            parser.Tuple: self.visit_tuple,
            parser.Output: self.visit_output
        }

    def visit(self, node):
        if type(node) in self._visit_fns:
            self._visit_fns[type(node)](node)

    def visit_output(self, node):
        pass

    def visit_result(self, node):
        pass

    def visit_result_record(self, node):
        pass

    def visit_value(self, node):
        pass

    def visit_cstring(self, node):
        pass

    def visit_list(self, node):
        pass

    def visit_tuple(self, node):
        pass


class PrettyPrintVisitor(BaseVisitor):

    class Indenter:
        def __init__(self):
            self._level = 0

        def __enter__(self):
            self._level += 1

        def __exit__(self, type_, value, traceback):
            self._level -= 1

        def __call__(self):
            return '  ' * self._level

    def __init__(self, outfile=sys.stdout, en_colors=False):
        super(PrettyPrintVisitor, self).__init__()
        self._outfile = outfile
        self._indent = PrettyPrintVisitor.Indenter()

        if en_colors:
            self._gos = PrettyPrintVisitor._get_out_str_colors
        else:
            self._gos = PrettyPrintVisitor._get_out_str_no_colors

    @staticmethod
    def _get_out_str_no_colors(s, c, attrs=[]):
        return s

    @staticmethod
    def _get_out_str_colors(s, c, attrs=[]):
        return colored(s, c, attrs=attrs)

    def _indent(self):
        self._outfile.write('  ' * self._indent)

    def visit_output(self, output):
        if output.result_record is not None:
            self.visit(output.result_record)

    def visit_result_record(self, rr):
        maybe_comma = ',' if len(rr.results) > 0 else ''
        ctoken = ''

        if rr.token is not None:
            ctoken = self._gos('{}'.format(rr.token.value), 'red', ['bold'])

        cresult_class = self._gos('^' + rr.result_class,
                                  'green', ['bold'])

        self._outfile.write('{}{}{}\n'.format(ctoken, cresult_class,
                                              maybe_comma))

        with self._indent:
            for i, result in enumerate(rr.results):
                self.visit(result)
                if i == len(rr.results) - 1:
                    self._outfile.write('\n')
                else:
                    self._outfile.write(',\n')

    def visit_result(self, result):
        cvariable_name = self._gos(result.variable.name, 'blue')
        self._outfile.write('{}{} = '.format(self._indent(), cvariable_name))
        self.visit(result.value)

    def visit_value(self, value):
        self.visit(value.value)

    def visit_cstring(self, cstring):
        cquote = self._gos('"', 'yellow')
        cvalue = self._gos(cstring.value, 'yellow', ['bold'])
        self._outfile.write('{quot}{val}{quot}'.format(quot=cquote, val=cvalue))

    def visit_list(self, list_):
        self._outfile.write('[\n')
        with self._indent:
            for i, element in enumerate(list_.elements):
                self.visit(element)
                if i == len(list_.elements) - 1:
                    self._outfile.write('\n')
                else:
                    self._outfile.write(',\n')
        self._outfile.write(self._indent())
        self._outfile.write(']')

    def visit_tuple(self, tuple_):
        self._outfile.write('{\n')
        with self._indent:
            for i, element in enumerate(tuple_.elements):
                self.visit(element)
                if i == len(tuple_.elements) - 1:
                    self._outfile.write('\n')
                else:
                    self._outfile.write(',\n')
        self._outfile.write(self._indent())
        self._outfile.write('}')

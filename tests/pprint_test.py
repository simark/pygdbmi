import unittest

from pygdbmi import parser
from pygdbmi import visitors

import io


class TestPPrintVisitor(unittest.TestCase):

    def setUp(self):
        pass

    def _test_pprint(self, input_, expected_output):
        f = io.StringIO()

        ast = parser.parse(input_)
        visitor = visitors.PrettyPrintVisitor(outfile=f)
        visitor.visit(ast)

        result = f.getvalue()

        self.assertEqual(result, expected_output)

    def test_simple(self):
        self._test_pprint('^done\n', '^done\n')
        self._test_pprint('^done,a="2"\n', '^done,\n  a = "2"\n')

    def test_one(self):
        input_ = '^done,numchild="2",displayhint="array",children=[child={' \
                 'name="var3.[0]",exp="[0]",numchild="1",type="my_class",' \
                 'thread-id="1"},child={name="var3.[1]",exp="[1]",numchild=' \
                 '"1",type="my_class",thread-id="1"}],has_more="0"\n'
        expected_output = \
            '^done,\n' \
            '  numchild = "2",\n' \
            '  displayhint = "array",\n' \
            '  children = [\n' \
            '    child = {\n' \
            '      name = "var3.[0]",\n' \
            '      exp = "[0]",\n' \
            '      numchild = "1",\n' \
            '      type = "my_class",\n' \
            '      thread-id = "1"\n' \
            '    },\n' \
            '    child = {\n' \
            '      name = "var3.[1]",\n' \
            '      exp = "[1]",\n' \
            '      numchild = "1",\n' \
            '      type = "my_class",\n' \
            '      thread-id = "1"\n' \
            '    }\n' \
            '  ],\n' \
            '  has_more = "0"\n'

        self._test_pprint(input_, expected_output)

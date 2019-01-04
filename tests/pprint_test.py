import unittest

from pygdbmi import parser
from pygdbmi import visitors

import io


class TestPPrintVisitor(unittest.TestCase):

    def setUp(self):
        pass

    def _test_pprint(self, input_, expected_output, strict):
        f = io.StringIO()

        ast = parser.parse(input_, strict)
        visitor = visitors.PrettyPrintVisitor(outfile=f, en_colors=False)
        visitor.visit(ast)

        result = f.getvalue()

        self.assertEqual(result, expected_output)

    def test_simple(self):
        self._test_pprint('^done\n(gdb)\n', '^done\n', True)
        self._test_pprint('^done,a="2"\n(gdb)\n', '^done,\n  a = "2"\n', True)
        self._test_pprint('712^exit\n', '712^exit\n', False)

    def test_one(self):
        input_ = '=breakpoint-created,bkpt={number="2",type="breakpoint",' \
                 'disp="keep",enabled="y",addr="<MULTIPLE>",times="0",' \
                 'original-location="add"},locations=[{number="2.1",' \
                 'enabled="y",addr="0x00000000004004e0",func="add(int, int)",' \
                 'file="/home/foo/bob.cc",fullname="/home/foo/bob.cc",' \
                 'line="21",thread-groups=["i1"]},{number="2.2",enabled="y",' \
                 'addr="0x00000000004004f8",func="add(double, double)",' \
                 'file="/home/foo/bob.cc",fullname="/home/foo/bob.cc",' \
                 'line="27",thread-groups=["i1"]}]\n' \
                 '4^done,numchild="2",displayhint="array",children=[child={' \
                 'name="var3.[0]",exp="[0]",numchild="1",type="my_class",' \
                 'thread-id="1"},child={name="var3.[1]",exp="[1]",numchild=' \
                 '"1",type="my_class",thread-id="1"}],has_more="0"\n'
        expected_output = \
            '=breakpoint-created,\n' \
            '  bkpt = {\n' \
            '    number = "2",\n' \
            '    type = "breakpoint",\n' \
            '    disp = "keep",\n' \
            '    enabled = "y",\n' \
            '    addr = "<MULTIPLE>",\n' \
            '    times = "0",\n' \
            '    original-location = "add"\n' \
            '  },\n' \
            '  locations = [\n' \
            '    {\n' \
            '      number = "2.1",\n' \
            '      enabled = "y",\n' \
            '      addr = "0x00000000004004e0",\n' \
            '      func = "add(int, int)",\n' \
            '      file = "/home/foo/bob.cc",\n' \
            '      fullname = "/home/foo/bob.cc",\n' \
            '      line = "21",\n' \
            '      thread-groups = [\n' \
            '        "i1"\n' \
            '      ]\n' \
            '    },\n' \
            '    {\n' \
            '      number = "2.2",\n' \
            '      enabled = "y",\n' \
            '      addr = "0x00000000004004f8",\n' \
            '      func = "add(double, double)",\n' \
            '      file = "/home/foo/bob.cc",\n' \
            '      fullname = "/home/foo/bob.cc",\n' \
            '      line = "27",\n' \
            '      thread-groups = [\n' \
            '        "i1"\n' \
            '      ]\n' \
            '    }\n' \
            '  ]\n' \
            '4^done,\n' \
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

        self._test_pprint(input_, expected_output, False)

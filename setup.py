#!/usr/bin/env python3
#
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

import os
import sys
import subprocess
from setuptools import setup
from setuptools import find_packages


# make sure we run Python 3+ here
v = sys.version_info
if v.major < 3:
    sys.stderr.write('Sorry, pygdbmi needs Python 3\n')
    sys.exit(1)

install_requires = [
    'pyPEG2',
]

console_scripts = [
   'gdb-mi-pprint=pygdbmi.cli.pprint:main'
]


setup(
    name='pygdbmi',
    version='0.0.1',
    description='GDB/MI parser/generator',
    author='Philippe Proulx',
    author_email='eeppeliteloop@gmail.com',
    license='MIT',
    keywords='gdb mi',
    url='https://github.com/eepp/pygdbmi',
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': console_scripts
    },
)

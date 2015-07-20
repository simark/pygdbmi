pygdbmi
=======

[![Build Status](https://travis-ci.org/simark/pygdbmi.svg?branch=master)](https://travis-ci.org/simark/pygdbmi)

**pygdbmi** is a Python 3 package for parsing and generating
[GDB/MI](https://sourceware.org/gdb/onlinedocs/gdb/GDB_002fMI.html)
data. It currently only supports parsing result records.


installing
----------

    git clone https://github.com/simark/pygdbmi.git && cd pygdbmi
    sudo ./setup install


CLI
---

pygdbmi ships with a command line tool, `gdb-mi-pprint`, which takes
a file containing GDB/MI output lines and pretty-prints them. Colored
output is supported using the `--colors` option if the `termcolor`
Python 3 package is installed.

CLI examples:

    gdb-mi-pprint my-data
    gdb-mi-pprint --colors my-data
    cat my-data | gdb-mi-pprint -
    cat my-data | gdb-mi-pprint - --colors
    
thanks
------
Many thanks to [Philippe Proulx](https://github.com/eepp) for writing the parser.

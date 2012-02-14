#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2011 Geisha Tokyo Entertainment, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "Software"), to deal in 
# the Software without restriction, including without limitation the rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
# the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import with_statement
import sys
from lxml import etree

sys.path.append('..')
from lightning_svg import LightningSvg

def xml2html(input, output):
    with open(input, 'r') as f_in:
        html, css, div = LightningSvg().xml2svg(f_in)
    with open(output, 'w') as f_out:
        f_out.write(html)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: %s <input(xml)> <output(html)>' % sys.argv[0]
        sys.exit(1)
    input = sys.argv[1]
    output = sys.argv[2]

    xml2html(input, output)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from vg.parser import SvgBuilder, Parser

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'usage: python %s inputfilename.xml output_directory' % sys.argv[0]
        sys.exit(1)

    fp = open(sys.argv[1], 'r')

    builder = SvgBuilder(fp, '', 1.0)
    builder.save(sys.argv[2])

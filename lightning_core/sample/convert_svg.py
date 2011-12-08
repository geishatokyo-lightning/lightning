#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.append('../..')
from lightning_core.vg.parser import SvgBuilder


def main(filepath, outdirname):
    builder = SvgBuilder(open(filepath,'r'))

    builder.save_as_static_svg(outdirname)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "Usage : <input xml> <output directory>"
        sys.exit()

    filepath = sys.argv[1]
    outdirname = sys.argv[2]

    main(filepath, outdirname)

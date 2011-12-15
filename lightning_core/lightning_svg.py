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

from vg.cssanim import AnimationManager
from vg.parser import SvgBuilder

class LightningSvg(object):

    # singleton
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            orig = super(LightningSvg, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    def make_html(self, div, css, anim):
        return '''<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="ja" xml:lang="ja">
<head>
<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8"></meta>
<title>lightning</title>
</head>
<body>
%s
<style type="text/css" rel="stylesheet">%s%s</style>
</body>
</html>
    ''' % (div, css, self.make_webkit_css(anim))

    def make_webkit_css(self, anims, sp='\n'):
        return sp.join(['.%s {-webkit-animation-name: %s;}' % (anim, anim) for anim in anims.split(',') if anim != ""])

    def xml2svg(self, filepath, mcname=None, key_prefix='', has_anim_name=True, scale=1.0):
        def make_tables(manager, filepath, key_prefix, mcname):
            builder = SvgBuilder(filepath, key_prefix, scale)

            shape_table = manager.get_shapes(builder.get_shapes().split('\n'))
            anim_table  = manager.get_animation(builder.get_animation())

            structure_table, structure_tree = manager.get_structure(builder.get_structure(),
                                                                    shape_table, anim_table,
                                                                    [], 
                                                                    builder.get_shapes_as_dict(),
                                                                    mcname,
                                                                    key_prefix)

            return shape_table, anim_table, structure_table, structure_tree


        html     = ''
        dir_path = '.'
        file_path = ''

        manager = AnimationManager(dir_path, file_path)

        shape_table, anim_table, structure_table, structure_tree = make_tables(manager, filepath, key_prefix, mcname)

        css   = manager.write_css(structure_table, shape_table, anim_table, key_prefix, has_anim_name)
        div   = manager.write_div(structure_tree)
        anims = ','.join(anim_table.keys())
        html = self.make_html(div, css, anims)

        if has_anim_name:
            return html, css, div
        else:
            return html, css, div, anims

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'usage: python %s input.xml output.xml' % sys.argv[0]
        sys.exit(1)
    inputfilepath = sys.argv[1]
    outputfilepath = sys.argv[2]
    fp = open(inputfilepath, 'r')
    html, css, div = LightningSvg().xml2svg(fp, mcname=None, key_prefix='', scale=1.0)
    with open(outputfilepath, 'w') as f:
        f.write(html)

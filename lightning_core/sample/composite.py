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

class LightningElement(object):
    def __init__(self, html, css, div, anims):
        self.html = html
        self.css = css
        self.div = div
        self.anims = anims

def composite(baseElm, newdiv):
    for elm in baseElm.iterfind('.//div'):
        if elm.get('id') == 'body':
            elm.getparent().replace(elm, etree.fromstring(newdiv))
    return baseElm

def get_lightning_element(filepath, mcname, key_prefix):
    with open(filepath, 'r') as f:
        return LightningElement(*(LightningSvg().xml2svg(f, mcname=mcname, key_prefix=key_prefix, has_anim_name=False, scale=1.0)))

def composite_html(base, part, output_path):
    comp_div = composite(etree.fromstring(base.div), part.div)
    html = LightningSvg().make_html(etree.tostring(comp_div), base.css+part.css, part.anims)
    with open(output_path, 'w') as f:
        f.write(html)

if __name__ == '__main__':
    base_element = get_lightning_element('samplexml_base.xml', mcname=None, key_prefix='base')
    myobj1_element = get_lightning_element('samplexml_myobj1.xml', mcname='body', key_prefix='myobj1')
    myobj2_element = get_lightning_element('samplexml_myobj2.xml', mcname='body', key_prefix='myobj2')

    composite_html(base_element, myobj1_element, 'merged1.html')
    composite_html(base_element, myobj2_element, 'merged2.html')


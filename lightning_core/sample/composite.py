#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from lxml import etree

sys.path.append('..')
from lightning_svg import LightningSvg

def composite(baseElm, newdiv):
  for elm in baseElm.iterfind('.//div'):
    if elm.get('id') == 'body':
      elm.getparent().replace(elm, etree.fromstring(newdiv))
  return baseElm

if __name__ == '__main__':

  basefile      = open('samplexml_base.xml', 'r')
  myobjectfile1 = open('samplexml_myobj1.xml', 'r')
  myobjectfile2 = open('samplexml_myobj2.xml', 'r')

  basehtml, basecss, basediv ,baseanims = LightningSvg().xml2svg(basefile,      mcname=None,   key_prefix='base' , has_anim_name=False, scale=1.0)
  myhtml1,  mycss1,  mydiv1,  myanims1  = LightningSvg().xml2svg(myobjectfile1, mcname="body", key_prefix='myobj', has_anim_name=False, scale=1.0)
  myhtml2,  mycss2,  mydiv2,  myanims2  = LightningSvg().xml2svg(myobjectfile2, mcname="body", key_prefix='myobj', has_anim_name=False, scale=1.0)

  basefile.close()
  myobjectfile1.close()
  myobjectfile2.close()

  newdiv1 = composite(etree.fromstring(basediv), mydiv1)
  newdiv2 = composite(etree.fromstring(basediv), mydiv2)

  html1 = LightningSvg().make_html(etree.tostring(newdiv1), basecss+mycss1, myanims1)
  html2 = LightningSvg().make_html(etree.tostring(newdiv2), basecss+mycss2, myanims2)

  with open('merged1.html', 'w') as f:
    f.write(html1)
  with open('merged2.html', 'w') as f:
    f.write(html2)

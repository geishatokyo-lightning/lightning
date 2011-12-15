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

from lightning_core.vg.lightningutil import *
import unittest


class TestLUtil(unittest.TestCase):

    # LUtil
    def test_get_values(self):
        keys = ('hoge','foo','bar')
        elm = dict(zip(keys, [None,'bar',0]))
        self.assertEqual(LUtil.get_values(elm, 'hoge', 'foo', 'bar'),[None,'bar',0])

        floatelm = dict(zip(keys, ['10.13145',None,0]))
        self.assertEqual(LUtil.get_values_as_float(floatelm, 'hoge', 'foo', 'bar'),[10.13145,None,0])
        intelm = dict(zip(keys, [10,None,0]))
        self.assertEqual(LUtil.get_values_as_int(intelm, 'hoge', 'foo', 'bar'),[10,None,0])

    def test_get_colortrans(self):
        colorNone = {}
        self.assertEqual(LUtil.get_colortrans(colorNone, 'factor'), [256,256,256,256])
        self.assertEqual(LUtil.get_colortrans(colorNone, 'offset'), [0,0,0,0])

        fcolor1 = {'factorRed':'256','factorGreen':'0','factorBlue':'255'}
        ocolor1 = {'offsetRed':256,'offsetGreen':0,'offsetBlue':255}
        self.assertEqual(LUtil.get_colortrans(fcolor1, 'factor'), [256,0,255,256])
        self.assertEqual(LUtil.get_colortrans(ocolor1, 'offset'), [256,0,255,0])

        fcolor2 = {'factorRed':13,'factorGreen':0,'factorBlue':16,'factorAlpha':200}
        ocolor2 = {'offsetRed':'13','offsetGreen':'0','offsetBlue':'16','offsetAlpha':'200'}
        self.assertEqual(LUtil.get_colortrans(fcolor2, 'factor'), [13,0,16,200])
        self.assertEqual(LUtil.get_colortrans(ocolor2, 'offset'), [13,0,16,200])

    def test__rgb_to_hex(self):
        self.assertEqual(LUtil.rgb_to_hex((0,1,-1,1)), '#000100')
        self.assertEqual(LUtil.rgb_to_hex((256,255,254,256)), '#fffffe')

    def test_get_transform_matrig(self):
        elm1 = {'scaleX':1.1111,'scaleY':2.345,'skewX':1000,'skewY':0.09,'transX':12,'transY':10}
        elm2 = {'scaleX':1.1111,'scaleY':2.345,'transX':12,'transY':10}
        self.assertEqual(LUtil.get_transform_matrix(elm1),[1.1111,1000,0.09,2.345,12,10])
        self.assertEqual(LUtil.get_transform_matrix(elm2),[1.1111,None,None,2.345,12,10])

    def test_make_key_string(self):
        objectID = '13'
        self.assertEqual(LUtil.make_key_string('13', 'hoge', 'fuga'),'hoge-13-fuga')

    def test_objectID_from_key(self):
        self.assertEqual(LUtil.objectID_from_key('hoge-13-fuga'), '13')

if __name__ == '__main__':
    unittest.main()

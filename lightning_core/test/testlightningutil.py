#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lightning.lightning.vg.lightningutil import *
import unittest


class TestLUtil(unittest.TestCase):

    # LUtil
    def test_get_values(self):
        keys = ('hoge','foo','bar')
        elm = dict(zip(keys, [None,'bar',0]))
        self.assertEqual(LUtil.get_values(elm, 'hoge', 'foo', 'bar'),[None,'bar',0])

        floatelm = dict(zip(keys, [10,None,0]))
        self.assertEqual(LUtil.get_values_as_float(floatelm, 'hoge', 'foo', 'bar'),[10.0,None,0])
        intelm = dict(zip(keys, [10,None,0]))
        self.assertEqual(LUtil.get_values_as_int(floatelm, 'hoge', 'foo', 'bar'),[10,None,0])

    def test_get_ctf(self):
        colorNone = {}
        self.assertEqual(LUtil.get_ctf(colorNone, 'factor'), [256,256,256,256])
        self.assertEqual(LUtil.get_ctf(colorNone, 'offset'), [0,0,0,0])

        fcolor1 = {'factorRed':'256','factorGreen':'0','factorBlue':'255'}
        ocolor1 = {'offsetRed':256,'offsetGreen':0,'offsetBlue':255}
        self.assertEqual(LUtil.get_ctf(fcolor1, 'factor'), [256,0,255,256])
        self.assertEqual(LUtil.get_ctf(ocolor1, 'offset'), [256,0,255,0])

        fcolor2 = {'factorRed':13,'factorGreen':0,'factorBlue':16,'factorAlpha':200}
        ocolor2 = {'offsetRed':'13','offsetGreen':'0','offsetBlue':'16','offsetAlpha':'200'}
        self.assertEqual(LUtil.get_ctf(fcolor2, 'factor'), [13,0,16,200])
        self.assertEqual(LUtil.get_ctf(ocolor2, 'offset'), [13,0,16,200])

    def test__rgb_to_hex(self):
        self.assertEqual(LUtil.rgb_to_hex((0,1,-1,1)), '#000100')
        self.assertEqual(LUtil.rgb_to_hex((256,255,254,256)), '#fffffe')


if __name__ == '__main__':
    unittest.main()

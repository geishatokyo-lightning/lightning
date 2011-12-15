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

import unittest
from lightning_core.vg.vg import *
from lightning_core.vg.parser import *
from lxml import etree

class TestLinearGrad(unittest.TestCase):

    def test_constructor(self):
        c1 = [256,256,256,256]
        c2 = [  0,  0,  0,  0]
        sp1 = Stop(c1, '100')
        sp2 = Stop(c2, '0')
        gtf = {'scaleX':'0', 'scaleY':'0.101'}
        lg = LinearGradient('100', gtf, (sp1,sp2))

        self.assertEqual(lg.get('id'), '100')
        self.assertEqual(lg.get('gradientUnits'), 'userSpaceOnUse')
        self.assertEqual(lg.get('x1'), '-819')
        self.assertEqual(lg.get('x2'), '819')
        self.assertEqual(lg.get('gradientTransform'), 'matrix(0.00 0.00 0.00 0.10 0.0000 0.0000)')

        self.assertEqual(len(lg), 2)

        self.assertEqual(lg[0].get('stop-color'), '#ffffff')
        self.assertEqual(lg[0].get('stop-opacity'), '1.0')
        self.assertEqual(lg[0].get('offset'), str(100.0/255))
        self.assertEqual(lg[1].get('stop-color'), '#000000')
        self.assertEqual(lg[1].get('stop-opacity'), str(0.0/255))
        self.assertEqual(lg[1].get('offset'), str(0.0/255))

class TestTransform(unittest.TestCase):

    def setUp(self):
        filename = './lightning_core/test/xmlsamples.xml'
        f = open(filename,'r')
        samplexml = f.read()
        self.poxml = etree.XML(samplexml).xpath('.//PLACE_OBJECT2_HAS_COLORTRANS/PlaceObject2')[0]
        self.transform = Transform()
        self.parser = Parser()
        self.po = self.parser._get_place_object(self.poxml)

    def test_constructor(self):
        transform = Transform()
        self.assertEqual(transform.sx, 1.0)
        self.assertEqual(transform.sy, 1.0)
        self.assertEqual(transform.tx, 0.0)
        self.assertEqual(transform.ty, 0.0)
        self.assertEqual(transform.wx, 0.0)
        self.assertEqual(transform.wy, 0.0)
        self.assertEqual(transform.ctf, [])
        self.assertEqual(transform.depth, 1)
        self.assertEqual(transform.clipDepth, None)
        self.assertEqual(transform.name, None)
        self.assertEqual(transform.visible, True)
    def test_set_items_and_get_matrix(self):
        transform = Transform()
        transform.set_items(self.po.items())
        self.assertEqual(transform.get_matrix(), (1.001770019531250, 0.0, 0.0, 1.0, -25.7, -57.0))

class TestTree(unittest.TestCase):
    def test_constructor(self):
        tree = Tree()
        self.assertAlmostEqual(tree.sx, 1.0)
        self.assertAlmostEqual(tree.sy, 1.0)
        self.assertAlmostEqual(tree.wx, 0.0)
        self.assertAlmostEqual(tree.wy, 0.0)
        self.assertAlmostEqual(tree.tx, 0.0)
        self.assertAlmostEqual(tree.ty, 0.0)
        self.assertEqual(len(tree.ctf), 0.0)
        self.assertEqual(tree.depth, 1)
        self.assertEqual(tree.name, None)
        self.assertEqual(len(tree.children), 0)
        self.assertEqual(tree.parent, None)

    def test_update(self):
        tree = Tree()
        tree.set_items({'tx':2.0})
        self.assertAlmostEqual(tree.tx, 2.0)

    def test_str(self):
        tree = Tree()
        self.assertEqual(str(tree), 'key=None\n')
        tree.key = 'hoge'
        self.assertEqual(str(tree), 'key=hoge\n')
        tree2 = Tree()
        tree2.key = 'fuga'
        tree.children.append(tree2)
        self.assertEqual(str(tree), 'key=hoge\n\tkey=fuga')


class TestAnimation(unittest.TestCase):
    def test_constructor(self):
        anim = Animation()
        self.assertEqual(anim.key, None)
        self.assertEqual(len(anim.frames), 0)

    def test_appendFrame(self):
        anim = Animation()
        index = 1
        sx = 1.0
        sy = 1.0
        wx = 0.0
        wy = 0.0
        tx = 0.0
        ty = 0.0
        ctf = []
        anim.key = 'hoge'
        anim.appendFrame(index, sx, sy, wx, wy, tx, ty, ctf)
        self.assertEqual(anim.key, 'hoge')
        self.assertEqual(len(anim.frames), 1)
        frame = anim.frames[0]
        self.assertEqual(frame['index'], 1)
        self.assertAlmostEqual(frame.sx, 1.0)
        self.assertAlmostEqual(frame['sy'], 1.0)
        self.assertAlmostEqual(frame['wx'], 0.0)
        self.assertAlmostEqual(frame['wy'], 0.0)
        self.assertAlmostEqual(frame['tx'], 0.0)
        self.assertAlmostEqual(frame['ty'], 0.0)
        self.assertEqual(frame['ctf'], [])

if __name__ == '__main__':
    unittest.main()

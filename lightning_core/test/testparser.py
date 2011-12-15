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
from lightning_core.vg.parser import *
from lxml import etree
import hashlib

class TestSvgBuilder(unittest.TestCase):
    def setUp(self):
        self.simplexmlfilename = './lightning_core/test/testfiles/a_mouth1Mc_000101.xml'

    def test_get_shapes(self):
        simplefile = open(self.simplexmlfilename,'r')
        builder = SvgBuilder(simplefile)
        m = hashlib.sha1()
        m.update(builder.parser.shapes['1'].symbol)
        self.assertEqual(builder.get_shapes(),'1\nobj1 %s 0 0 535 182\n' % m.hexdigest())

    def test_get_structure(self):
        simplefile = open(self.simplexmlfilename,'r')
        builder = SvgBuilder(simplefile)
        self.assertEqual(builder.get_structure().tag,'structure')

class TestParser(unittest.TestCase):

    def setUp(self):
        filename = './lightning_core/test/xmlsamples.xml'
        f = open(filename,'r')
        self.samplexml = f.read()
        self.simplexmlfilename = './lightning_core/test/testfiles/a_mouth1Mc_000101.xml'
        simplefile = open(self.simplexmlfilename,'r')
        self.simplexml = simplefile.read()

    def _get_xml(self, samplename, objectname):
        parser = Parser()
        xml = etree.XML(self.samplexml).xpath('.//%s/%s' % (samplename,objectname))[0]
        return xml

    def sample_sprite(self):
        frame = Frame()
        matrixDict = {'sx': 4.0, 'sy': 4.0, 'wx':0 , 'wy': 0, 'tx': -2.0, 'ty': -2.0, 'ctf':[], 'depth': 3,'clipDepth':3}
        symbols = ['test']
        name = 'hoge'
        frame.addPlace(matrixDict, symbols, name)
        sprite = Sprite()
        sprite.addFrame(frame)
        return sprite

    def test__search_shape(self):
        parser = Parser()
        key = 'obj1'
        shape = parser._search_shape(key)
        self.assertEqual(shape, None)
        parser.shapes['1'] = 'shape'
        shape = parser._search_shape(key)
        self.assertEqual(shape, 'shape')
        
    def test__search_sprite(self):
        parser = Parser()
        key = 'obj1'
        sprite = parser._search_sprite(key)
        self.assertEqual(sprite, None)
        parser.sprites['1'] = 'sprite'
        sprite = parser._search_sprite(key)
        self.assertEqual(sprite, 'sprite')

    def test__get_styles_colors_solid(self):
        parser = Parser()
        shape = Shape()
        num = 0
        xml = self._get_xml('SOLID_COLOR_SIMPLE', 'styles/StyleList')
        colorElms = xml.xpath(".//fillStyles")

        colors = parser._get_styles_colors(colorElms, shape, num)
        self.assertEquals(len(colors), 1)

    def test__get_styles_gradient_1(self):
        parser = Parser()
        xml = self._get_xml('LINEAR_GRADIENT_1', 'styles/StyleList')
        gradElms1 = xml.xpath(".//LinearGradient")[0]
        lgrad1 = parser._get_styles_gradient(gradElms1, 'hogefuga')
        self.assert_lineargrad(lgrad1, 'hogefuga', 'matrix(0.04 0.00 0.00 0.03 33.3500 28.3000)')
        for (i, ge) in zip(range(len(lgrad1)), lgrad1.iter('stop')):
            if i == 0:
                self.assert_stop(ge, '#ffffff', '0.0','0.0274509803922')
            elif i == 1:
                self.assert_stop(ge, '#e9532e', '1.0','0.98431372549')


    def test__get_styles_gradient_2(self):
        num = 1
        parser = Parser()
        shape = Shape()
        shape.symbol = 'fuga'
        xml = self._get_xml('LINEAR_GRADIENT_2', 'styles/StyleList')
        colorElms = xml.xpath(".//fillStyles")

        colors = parser._get_styles_colors(colorElms, shape, num)
        gradElem = shape.defs[0]
        self.assert_lineargrad(gradElem, '%s_%d' % (shape.symbol, num), 'matrix(0.00 0.01 -0.01 0.00 0.0000 -12.2000)')
        for (i, ge) in zip(range(len(gradElem)), gradElem.iter('stop')):
            if i == 0:
                self.assert_stop(ge, '#ffffff', '0.0','0.0')
            elif i == 1:
                self.assert_stop(ge, '#3399ff', '1.0','1.0')

    def assert_lineargrad(self, gradElem, objectId, gtf):
        self.assertEquals(gradElem.get('id'), objectId)
        self.assertEquals(gradElem.get('x1'), '-819')
        self.assertEquals(gradElem.get('x2'),  '819')
        self.assertEquals(gradElem.get('gradientUnits') ,'userSpaceOnUse')
        self.assertEquals(gradElem.get('gradientTransform'), gtf)

    def assert_stop(self, ge, c, o, offset):
        self.assertEquals(ge.get('stop-color'), c)
        self.assertEquals(ge.get('stop-opacity'), o)
        self.assertEquals(ge.get('offset'), offset)

    def test__proc_define_shape_1(self):
        # simple test
        parser = Parser()
        xml = self._get_xml('DEFINE_SHAPE_SIMPLE', 'DefineShape')
        parser._proc_define_shape(xml)
        values = parser.shapes['138'].edges[0].values
        # Shape
        self.assertEqual(values[0]['fr'], 0)
        self.assertEqual(values[0]['fl'], None)
        self.assertEqual(values[0]['ln'], None)
        self.assertEqual(values[0]['type'], 'S')
        self.assertEqual(values[0]['x'], 13.0)
        self.assertEqual(values[0]['y'], -13.0)
        # Curv
        self.assertEqual(values[1]['type'], 'C')
        self.assertEqual(values[1]['x1'], 0)
        self.assertEqual(values[1]['x2'], -3.8)
        self.assertEqual(values[1]['y1'], 5.4)
        self.assertEqual(values[1]['y2'], 3.8)
        # LineTo
        self.assertEqual(values[2]['type'], 'L')
        self.assertEqual(values[2]['x'], 0)
        self.assertEqual(values[2]['y'], 240)

        shape = parser.shapes['138']
        self.assertEqual(shape.left,-260)
        self.assertEqual(shape.right,260)
        self.assertEqual(shape.top,-520)
        self.assertEqual(shape.bottom,0)
        self.assertEqual(shape.width,520)
        self.assertEqual(shape.height,520)
        self.assertEqual(shape.symbol,'obj138')
        self.assertEqual(shape.edges[0].colors[0], {'s':(255, 0, 0, 256)})

    def test__proc_define_shape_2(self):
        # simple test
        parser = Parser()
        xml = self._get_xml('DEFINE_SHAPE_2', 'DefineShape2')
        parser._proc_define_shape(xml)
        edges = parser.shapes['47'].edges
        self.assertEqual(len(edges), 4)

        self.assertEqual(len(edges[0].values), 13)
        self.assertEqual(len(edges[1].values), 2)
        self.assertEqual(len(edges[2].values), 2)
        self.assertEqual(len(edges[3].values), 6)

        self.assertEqual(edges[0].colors, [{'s':(255,215,171,256)}])
        self.assertEqual(edges[1].colors, [{'l':(155,129,107,256)}])
        self.assertEqual(edges[2].colors, [{'l':(155,129,107,256)}])
        self.assertEqual(edges[3].colors, [{'s':(239,188,154,256)}])

        self.assertEqual(edges[0].lineWidths, [])
        self.assertEqual(edges[1].lineWidths, [1.0])
        self.assertEqual(edges[2].lineWidths, [1.0])
        self.assertEqual(edges[3].lineWidths, [])

    def test__proc_define_shape_2_2(self):
        parser = Parser()
        xml = self._get_xml('DEFINE_SHAPE_2_2', 'DefineShape2')
        parser._proc_define_shape(xml)
        edges = parser.shapes['79'].edges

        self.assertEqual(len(edges), 2)

        self.assertEqual(edges[0].colors, [{'s':(158,84,48,256)},{'l':(103,122,104,256)}])
        self.assertEqual(edges[1].colors, [{'l':(255,255,255,256)}])

        self.assertEqual(len(edges[0].values), 13)
        self.assertEqual(len(edges[1].values), 6)

        self.assertEqual(edges[0].lineWidths, [1.0])
        self.assertEqual(edges[1].lineWidths, [1.0])

        self.assertEqual(edges[0].values[0]['type'], 'S')
        self.assertEqual(edges[0].values[1]['type'], 'C')
        self.assertEqual(edges[0].values[2]['type'], 'C')
        self.assertEqual(edges[0].values[3]['type'], 'C')
        self.assertEqual(edges[0].values[4]['type'], 'C')
        self.assertEqual(edges[0].values[5]['type'], 'C')
        self.assertEqual(edges[0].values[0]['type'], 'S')
        self.assertEqual(edges[0].values[1]['type'], 'C')
        self.assertEqual(edges[0].values[2]['type'], 'C')
        self.assertEqual(edges[0].values[3]['type'], 'C')
        self.assertEqual(edges[0].values[4]['type'], 'C')
        self.assertEqual(edges[0].values[5]['type'], 'C')
        self.assertEqual(edges[0].values[6]['type'], 'C')
        self.assertEqual(edges[0].values[7]['type'], 'C')
        self.assertEqual(edges[0].values[8]['type'], 'L')
        self.assertEqual(edges[0].values[9]['type'], 'C')
        self.assertEqual(edges[0].values[10]['type'], 'C')
        self.assertEqual(edges[0].values[11]['type'], 'L')
        self.assertEqual(edges[0].values[12]['type'], 'C')

        self.assertEqual(edges[1].values[0]['type'], 'S')
        self.assertEqual(edges[1].values[1]['type'], 'C')
        self.assertEqual(edges[1].values[2]['type'], 'C')
        self.assertEqual(edges[1].values[3]['type'], 'C')
        self.assertEqual(edges[1].values[4]['type'], 'C')
        self.assertEqual(edges[1].values[5]['type'], 'S')

    def test__proc_define_shape_3(self):
        parser = Parser()
        xml = self._get_xml('DEFINE_SHAPE_3', 'DefineShape3')
        parser._proc_define_shape(xml)
        edges = parser.shapes['128'].edges

        self.assertEqual(len(edges), 3)

        self.assertEqual(edges[0].colors, [{'s':(243,255,253,71)}])
        self.assertEqual(edges[1].colors, [{'s':(243,255,253,71)}])
        self.assertEqual(edges[2].colors, [{'s':(190,40,40,255)},{'s':(68,71,70,255)}])

 
    def test__get_styles_lines(self):
        parser = Parser()
        xml = self._get_xml('LINE_COLOR_SIMPLE', 'lineStyles')
        lineElms = xml.xpath(".//LineStyle")
        colors, widths= parser._get_styles_lines(lineElms)
        self.assertEquals(len(colors), 1)
        self.assertEquals(colors[0], (18, 28, 38, 256))
        self.assertEquals(widths[0], 1.0)


    #TODO:implement
    def test_make_svg(self):
        parser = Parser()
        parser.parse_from_str(self.simplexml)

    def test_str_shape_as_svg(self):
        parser = Parser()
        parser.parse_from_str(self.simplexml)
        e = etree.Element('fuga')
        svg = parser.str_shape_as_svg(parser.shapes['1'])
        self.assertEqual(svg.get('version'), '1.1')
        self.assertEqual(svg.get('viewBox'), '0.000000 0.000000 26.750000 9.100000')
        for defs in svg.iter('defs'):
            for fuga in defs.iter('fuga'):
                self.assertEqual(fuga, e)
        for g in svg.iter('g'):
            self.assertEqual(g.tag, 'g')

    def test_add_tree(self):
        parser = Parser()
        tree = Tree()
        tree.key = 'hoge'
        tree.tx = -0.3
        tree.ty = -3.0
        tree.wx = 100
        ch_tree = Tree()
        ch_tree.key = 'fuga'
        ch_tree.sx = 0.2
        ch_tree.sy = 2.0
        tree.children.append(ch_tree)
        element = etree.Element('Animation')
        parser.add_tree(tree, element)
        print etree.tostring(element, pretty_print=True)

        self.assertEqual(len(element), 1)
        self.assertEqual(element[0].tag, 'part')
        self.assertEqual(element[0].get('key'), 'hoge')
        self.assertAlmostEqual(float(element[0].get('tx')), -0.3)
        self.assertAlmostEqual(float(element[0].get('ty')), -3.0)
        self.assertAlmostEqual(float(element[0].get('wx')), 100)
        self.assertAlmostEqual(float(element[0].get('wy')), 0.0) # because tree.wy default is 0.0
        self.assertEqual(element[0].get('name'), None)
        self.assertEqual(element[0].get('clipDepth'), None)
        self.assertEqual(element[0].get('visible'), 'True') # because tree.visible default is True
        self.assertEqual(len(element[0]), 1)

        self.assertEqual(element[0][0].tag, 'part')
        self.assertEqual(element[0][0].get('key'), 'fuga')
        self.assertEqual(element[0][0].get('name'), None)
        self.assertEqual(element[0][0].get('clipDepth'), None)
        self.assertEqual(element[0][0].get('visible'), 'True') # because tree.visible default is True
        self.assertAlmostEqual(float(element[0][0].get('sx')), 0.2)
        self.assertAlmostEqual(float(element[0][0].get('sy')), 2.0)
        self.assertAlmostEqual(float(element[0][0].get('wx')), 0.0) # because tree.wx default is 0.0
        self.assertAlmostEqual(float(element[0][0].get('wy')), 0.0) # because tree.wy default is 0.0

    def test__set_vals(self):
        parser = Parser()
        part = etree.Element("part")
        parser._set_vals(part, hoge='fuga', foo=0, hage=None)
        self.assertEqual(part.get('hoge'), 'fuga')
        self.assertEqual(part.get('foo'), '0')
        self.assertEqual(part.get('hage'), None)

    def test_none_str_animation(self):
        parser = Parser()
        animations = parser._str_animation([], None)
        self.assertEqual(len(animations), 0)

    def test_default_str_animation(self):
        parser = Parser()
        all_symbols = ['test']
        frame = Frame()
        sprite = Sprite()
        sprite.addFrame(frame)
        animations = parser._str_animation(all_symbols, sprite)
        self.assertEqual(len(animations), 1)
        animation = animations['test']
        self.assertEqual(animation.key, None)
        self.assertEqual(len(animation.frames), 1)
        frame = animation.frames[0]
        self.assertAlmostEqual(frame.sx, 1.0)
        self.assertAlmostEqual(frame.sy, 1.0)
        self.assertAlmostEqual(frame.wx, 0.0)
        self.assertAlmostEqual(frame.wy, 0.0)
        self.assertAlmostEqual(frame.tx, 0.0)
        self.assertAlmostEqual(frame.ty, 0.0)
        self.assertEqual(frame.ctf, [])

    def test__str_animation(self):
        parser = Parser()
        all_symbols = ['test']
        sprite = self.sample_sprite()
        animations = parser._str_animation(all_symbols, sprite)
        self.assertEqual(len(animations), 1)
        animation = animations['test']
        self.assertEqual(animation.key, None)
        self.assertEqual(len(animation.frames), 1)
        frame = animation.frames[0]
        self.assertAlmostEqual(frame.sx, 4.0)
        self.assertAlmostEqual(frame.sy, 4.0)
        self.assertAlmostEqual(frame.wx, 0.0)
        self.assertAlmostEqual(frame.wy, 0.0)
        self.assertAlmostEqual(frame.tx, -2.0)
        self.assertAlmostEqual(frame.ty, -2.0)
        self.assertEqual(frame.ctf, [])

    def test__get_place_object_simple(self):
        parser = Parser()
        xml = self._get_xml('PLACE_OBJECT2_SIMPLE', 'PlaceObject2')
        po = parser._get_place_object(xml)
        self.assertAlmostEqual(po['tx'], -275.0)
        self.assertAlmostEqual(po['ty'],  166.0)
        self.assertEqual(po['sx'], -0.2713775634765625)
        self.assertEqual(po['sy'],  0.0)
        self.assertEqual(po['wx'], 0.0)
        self.assertEqual(po['wy'], 0.9611511230468750)
        self.assertEqual(po['depth'], 103)
        self.assertEqual(po['name'], 'a_leftHandAll')
        self.assertEqual(po['clipDepth'], None)
        self.assertEqual(po['ctf'], [])
        self.assertEqual(po['id'], '101')

    def test__get_place_object_complex(self):
        parser = Parser()
        xml = self._get_xml('PLACE_OBJECT2_HAS_COLORTRANS', 'PlaceObject2')
        po = parser._get_place_object(xml)
        self.assertEqual(po['sx'], 1.001770019531250)
        self.assertEqual(po['sy'], 1.0)
        self.assertEqual(po['wx'], None)
        self.assertEqual(po['wy'], None)
        self.assertEqual(po['tx'], -514.0)
        self.assertEqual(po['ty'], -1140.0)
        self.assertEqual(po['depth'], 19)
        self.assertEqual(po['name'], None)
        self.assertEqual(po['clipDepth'], None)
        self.assertEqual(po['ctf'], [205, 205, 256, 256, 80, 10, -20, 0])
        self.assertEqual(po['id'], '3')

    def test__proc_place_object(self):
        parser = Parser()
        xml = self._get_xml('PLACE_OBJECT2_SIMPLE', 'PlaceObject2')
        self.assertEqual(parser.places, {})
        parser._proc_place_object(xml)
        self.assertNotEqual(parser.places, {})

    def test__proc_define_sprite(self):
        parser = Parser()
        xml = self._get_xml('SPRITE_SIMPLE', 'DefineSprite')
        parser._proc_define_sprite(xml)
        sprite = parser.sprites['2']
        self.assertEqual(len(sprite.frames), 1)
        frame = sprite.frames[0]
        self.assertEqual(len(frame.places), 1)
        po = frame.places[0]
        self.assertEqual(po['depth'], 3)
        self.assertEqual(po['tx'], -1.0)
        self.assertEqual(po['ty'],  2.0)
        self.assertEqual(po['sx'], None)
        self.assertEqual(po['sy'], None)
        self.assertEqual(po['wx'], None)
        self.assertEqual(po['wy'], None)
        self.assertEqual(po['name'], None)
        self.assertEqual(po['clipDepth'], None)
        self.assertEqual(po['ctf'], [])

    def test__proc_define_sprite_2(self):
        parser = Parser()
        xml = etree.XML(open('./lightning_core/test/testfiles/goods_0777_sprite17.txt').read())
        parser._proc_define_sprite(xml)
        sprite = parser.sprites['17']
        self.assertEqual(len(sprite.frames), 21)
        places_length_list = [
            6,4,4,3,3, 6,6,6,6,6,
            3,3,3,3,3, 3,3,3,1,1, 1
        ]
        for i, length in enumerate(places_length_list):
            self.assertEqual(len(sprite.frames[i].places), length)
        self.assertEqual(len(sprite.frames[0].places[0].symbols), 1)
        self.assertEqual(sprite.frames[0].places[0].symbols[0], '-obj4-1')
        self.assertEqual(sprite.frames[0].places[1].symbols[0], '-obj10-3')
        self.assertEqual(sprite.frames[0].places[2].symbols[0], '-obj14-24')
        self.assertEqual(sprite.frames[0].places[3].symbols[0], '-obj16-29')
        self.assertEqual(sprite.frames[0].places[4].symbols[0], '-obj16-31')
        self.assertEqual(sprite.frames[0].places[5].symbols[0], '-obj16-33')

        self.assertEqual(sprite.frames[1].places[0].symbols[0], '-obj10-3')
        self.assertEqual(sprite.frames[1].places[1].symbols[0], '-obj16-29')
        self.assertEqual(sprite.frames[1].places[2].symbols[0], '-obj16-31')
        self.assertEqual(sprite.frames[1].places[3].symbols[0], '-obj16-33')

    def test_make_shape_element(self):
        parser = Parser()
        xml = self._get_xml('DEFINE_SHAPE_LINETO', 'DefineShape')
        parser._proc_define_shape(xml)
        shape = parser.shapes['1']
        gtag = Parser.ShapeMaker.make_shape_element(shape, [], 'hoge')
        for path in gtag.getchildren():
            self.assertEqual(path.get('clip-rule'), 'evenodd')
            self.assertEqual(path.get('fill'), '#66ccff')
            self.assertEqual(path.get('d'), 'M240.0000 0.0000 l-240.0000 -0.0000 l-0.0000 240.0000 l240.0000 -0.0000 l-0.0000 -240.0000 ')

    def test_make_shape_element_complex(self):
        parser = Parser()
        xml = self._get_xml('DEFINE_SHAPE_2_2', 'DefineShape2')
        parser._proc_define_shape(xml)
        shape = parser.shapes['79']
        gtag = Parser.ShapeMaker.make_shape_element(shape, [], 'hoge')
        for i,path in zip(xrange(len(gtag.getchildren())),gtag.getchildren()):
            self.assertEqual(path.get('clip-rule'), 'evenodd')
            if i==0:
                self.assertEqual(path.get('stroke-width'), "1.0")
                self.assertEqual(path.get('stroke-opacity'), "undefined")
                self.assertEqual(path.get('stroke'), "#677a68")
            elif i==1:
                self.assertEqual(path.get('fill'), "#9e5430")
            elif i==3:
                self.assertEqual(path.get('stroke-width'), "1.0")
                self.assertEqual(path.get('stroke-opacity'), "undefined")
                self.assertEqual(path.get('stroke'), "#ffffff")

    def test__path_data(self):
        edges = []
        edges.append({'y': 134.49999999999991, 'x': 61.40000000000007, 'type': 'S'})
        edges.append({'y': -0.45, 'x': -0.35, 'type': 'L'})
        edges.append({'y1': -0.1, 'x2': -3.2, 'x1': -0.5, 'type': 'C', 'y2': -2.05})
        edges.append({'fr': None, 'ln': None, 'type': 'S', 'y': 144.8, 'x': 163.05, 'fl': 0})
        edges.append({'y': -1.05, 'x': 0.85, 'type': 'L'})
        edges.append({'y1': -2.1, 'x2': 0.85, 'x1': 1.2, 'type': 'C', 'y2': -0.3})
        data = Parser.ShapeMaker._path_data(edges)
        self.assertEquals(data, 'M61.4000 134.5000 l-0.3500 -0.4500 q-0.5000 -0.1000 -3.7000 -2.1500 M163.0500 144.8000 l0.8500 -1.0500 q1.2000 -2.1000 2.0500 -2.4000 ')

    def test__reverse(self):
        path1 = []
        path2 = []
        path1.append({'fr': 0, 'ln': None, 'type': 'S', 'y': 177.2, 'x': 107.4, 'fl': None})
        path1.append({'y': -0.5, 'x': 3.1, 'type': 'L'})
        path1.append({'y': -0.7, 'x': 5.35, 'type': 'L'})
        path1.append({'y': -1.4, 'x': 6.15, 'type': 'L'})
        path1.append({'y1': -1.15, 'x2': 2.9, 'x1': 3.45, 'type': 'C', 'y2': -2.15})
        path1.append({'y1': -1.25, 'x2': 1.85, 'x1': 1.6, 'type': 'C', 'y2': 0.5})
        path1.append({'y1': 0.3, 'x2': 0.7, 'x1': 1.15, 'type': 'C', 'y2': 0.75})
        path1.append({'y1': 0.4, 'x2': 0.1, 'x1': 0.45, 'type': 'C', 'y2': 0.9})
        path1.append({'y1': 1.0, 'x2': -0.55, 'x1': 0.05, 'type': 'C', 'y2': 0.4})
        path1.append({'y1': 0.9, 'x2': -4.3, 'x1': -1.2, 'type': 'C', 'y2': 1.6})
        path1.append({'y1': 2.15, 'x2': -4.55, 'x1': -5.5, 'type': 'C', 'y2': 0.6})
        path1.append({'y1': 0.25, 'x2': -4.65, 'x1': -1.8, 'type': 'C', 'y2': -1.25})
        path1.append({'y': -1.35, 'x': -4.3, 'type': 'L'})
        path2.append({'fr': None, 'ln': None, 'type': 'S', 'y': 177.20000000000002, 'x': 107.39999999999999, 'fl': None})
        path = path1 + path2
        ps = []
        pl = []
        pc = []
        for p in path:
            if p["type"] == "S":
                ps.append(p)
            elif p["type"] == "L":
                pl.append(p)
            elif p["type"] == "C":
                pc.append(p)

        result = Parser.ShapeMaker._reverse(path)
        rs = []
        rl = []
        rc = []
        for r in result:
            if r["type"] == "S":
                rs.append(r)
            elif r["type"] == "L":
                rl.append(r)
            elif r["type"] == "C":
                rc.append(r)

        get_sum_x = lambda c: c["x"] if c.has_key("x") else c["x1"] + c["x2"]
        get_sum_y = lambda c: c["y"] if c.has_key("y") else c["y1"] + c["y2"]
        xlist = map(get_sum_x, path1)
        ylist = map(get_sum_y, path1)

        # Shape
        self.assertEqual(rs[0]["x"],sum(xlist))
        self.assertEqual(rs[0]["y"],sum(ylist))
        self.assertEqual(rs[1]["x"],ps[1]["x"])
        self.assertEqual(rs[1]["y"],ps[1]["y"])
        # LineTo
        for i in xrange(len(pl)):
            self.assertAlmostEqual(rl[len(rl)-1-i]["x"], -pl[i]["x"])
            self.assertAlmostEqual(rl[len(rl)-1-i]["y"], -pl[i]["y"])
        # CurveTo
        for i in xrange(len(pc)):
            self.assertAlmostEqual(rc[len(rc)-1-i]["x2"], -pc[i]["x1"])
            self.assertAlmostEqual(rc[len(rc)-1-i]["y2"], -pc[i]["y1"])
            self.assertAlmostEqual(rc[len(rc)-1-i]["x1"], -pc[i]["x2"])
            self.assertAlmostEqual(rc[len(rc)-1-i]["y1"], -pc[i]["y2"])

    def test__merge_path(self):
        path = []
        path.append({'fr': None, 'ln': None, 'type': 'S', 'y': 267.6, 'x': 79.15, 'fl': 0})
        path.append({'y': 2.4, 'x': 2.1, 'type': 'L'})
        path.append({'y': -1.5, 'x': -0.4, 'type': 'L'})
        path.append({'y': -0.9, 'x': -1.7, 'type': 'L'})
        result = Parser.ShapeMaker._merge_path(path)
        self.assertEqual(result,[path])
        path2=[]
        path2.append({'fr': None, 'ln': None, 'type': 'S', 'y': 83.75, 'x': 164.75, 'fl': 0})
        path2.append({'y1': -4.3, 'x2': -3.15, 'x1': -0.3, 'type': 'C', 'y2': -8.35})
        path2.append({'y1': -9.3, 'x2': -3.7, 'x1': -3.55, 'type': 'C', 'y2': -4.4})
        path2.append({'y': -2.35, 'x': -2.25, 'type': 'L'})
        path2.append({'y1': 12.05, 'x2': -1.75, 'x1': 2.7, 'type': 'C', 'y2': 4.3})
        path2.append({'y1': 2.95, 'x2': -2.05, 'x1': -1.2, 'type': 'C', 'y2': 1.9})
        path2.append({'y': -6.15, 'x': -3.75, 'type': 'L'})
        path2.append({'y1': -5.45, 'x2': -5.6, 'x1': -3.55, 'type': 'C', 'y2': -6.15})
        path2.append({'y': -5.1, 'x': -4.85, 'type': 'L'})
        path2.append({'y': 9.65, 'x': 5.6, 'type': 'L'})
        path2.append({'y1': 10.65, 'x2': 2.35, 'x1': 6.05, 'type': 'C', 'y2': 5.05})
        path2.append({'y': 0.8, 'x': -1.85, 'type': 'L'})
        path2.append({'y1': -4.9, 'x2': -2.65, 'x1': -2.85, 'type': 'C', 'y2': -2.9})
        path2.append({'y': -7.65, 'x': -7.35, 'type': 'L'})
        path2.append({'y': 6.9, 'x': 4.05, 'type': 'L'})
        path2.append({'y1': 7.35, 'x2': 0.2, 'x1': 4.1, 'type': 'C', 'y2': 2.05})
        path2.append({'y': 0.45, 'x': 0.05, 'type': 'L'})
        path2.append({'y1': 1.25, 'x2': -8.9, 'x1': -5.75, 'type': 'C', 'y2': 0.05})
        path2.append({'y1': -5.8, 'x2': -3.15, 'x1': -1.9, 'type': 'C', 'y2': -4.6})
        path2.append({'y1': -6.35, 'x2': -7.7, 'x1': -4.3, 'type': 'C', 'y2': -9.65})
        path2.append({'y1': 3.15, 'x2': 3.3, 'x1': 2.35, 'type': 'C', 'y2': 9.1})
        path2.append({'y1': 8.65, 'x2': 0.95, 'x1': 3.2, 'type': 'C', 'y2': 5.25})
        path2.append({'y1': -0.95, 'x2': -4.75, 'x1': -13.55, 'type': 'C', 'y2': -6.5})
        path2.append({'y1': -2.3, 'x2': -1.1, 'x1': -1.7, 'type': 'C', 'y2': -3.7})
        path2.append({'y': -6.05, 'x': -1.7, 'type': 'L'})
        path2.append({'y': -0.65, 'x': 0.0, 'type': 'L'})
        path2.append({'y': 4.1, 'x': -1.4, 'type': 'L'})
        path2.append({'y1': 4.5, 'x2': -0.4, 'x1': -1.5, 'type': 'C', 'y2': 2.05})
        path2.append({'y': 9.35, 'x': -1.95, 'type': 'L'})
        path2.append({'y1': 4.0, 'x2': 1.15, 'x1': 1.0, 'type': 'C', 'y2': 2.6})
        path2.append({'y1': 2.5, 'x2': 0.0, 'x1': 1.1, 'type': 'C', 'y2': -1.45})
        path2.append({'y1': -1.85, 'x2': 0.7, 'x1': 0.0, 'type': 'C', 'y2': -8.4})
        path2.append({'y': -8.05, 'x': 0.65, 'type': 'L'})
        path2.append({'y': 21.0, 'x': 4.65, 'type': 'L'})
        path2.append({'y': -1.1, 'x': 10.7, 'type': 'L'})
        path2.append({'y1': -1.35, 'x2': 1.05, 'x1': 10.95, 'type': 'C', 'y2': -1.25})
        path2.append({'y1': -1.2, 'x2': -1.75, 'x1': 1.0, 'type': 'C', 'y2': -6.95})
        path2.append({'y': -5.15, 'x': -1.25, 'type': 'L'})
        path2.append({'y': 13.3, 'x': 5.95, 'type': 'L'})
        path2.append({'y': -1.65, 'x': 38.35, 'type': 'L'})
        path2.append({'y': 0.4, 'x': 0.6, 'type': 'L'})
        path2.append({'y1': -0.25, 'x2': -0.2, 'x1': 0.6, 'type': 'C', 'y2': -3.15})
        path2.append({'fr': None, 'ln': None, 'type': 'S', 'y': 70.4, 'x': 88.1, 'fl': None})
        path2.append({'y1': 4.4, 'x2': 1.3, 'x1': -0.15, 'type': 'C', 'y2': 5.95})
        path2.append({'y': -6.35, 'x': -0.5, 'type': 'L'})
        path2.append({'y1': -3.3, 'x2': 2.35, 'x1': -0.4, 'type': 'C', 'y2': -8.35})
        path2.append({'y': -7.65, 'x': 2.4, 'type': 'L'})
        path2.append({'y': 4.0, 'x': -5.7, 'type': 'L'})
        path2.append({'y1': 5.0, 'x2': -5.2, 'x1': -6.75, 'type': 'C', 'y2': 5.0})
        path2.append({'y1': 2.7, 'x2': -1.6, 'x1': -2.85, 'type': 'C', 'y2': 2.7})
        path2.append({'y1': 0.15, 'x2': -2.55, 'x1': -3.0, 'type': 'C', 'y2': -2.6})
        path2.append({'y1': 6.85, 'x2': 0.55, 'x1': -1.7, 'type': 'C', 'y2': 8.25})
        path2.append({'y1': 5.85, 'x2': 1.1, 'x1': 0.4, 'type': 'C', 'y2': 3.5})
        path2.append({'y': 0.9, 'x': 0.3, 'type': 'L'})
        path2.append({'y': -22.0, 'x': 9.35, 'type': 'L'})
        path2.append({'y1': -3.9, 'x2': 6.55, 'x1': 1.95, 'type': 'C', 'y2': -6.25})
        path2.append({'y': -5.5, 'x': 6.15, 'type': 'L'})
        path2.append({'y': 3.45, 'x': -0.9, 'type': 'L'})
        path2.append({'y1': 4.1, 'x2': -0.15, 'x1': -0.95, 'type': 'C', 'y2': 3.1})
        result2 = Parser.ShapeMaker._merge_path(path2)
        self.assertEqual(result2,[[{'fr': None, 'ln': None, 'type': 'S', 'y': 70.4, 'x': 88.1, 'fl': None}, {'y1': 4.4, 'x2': 1.3, 'x1': -0.15, 'type': 'C', 'y2': 5.95}, {'y': -6.35, 'x': -0.5, 'type': 'L'}, {'y1': -3.3, 'x2': 2.35, 'x1': -0.4, 'type': 'C', 'y2': -8.35}, {'y': -7.65, 'x': 2.4, 'type': 'L'}, {'y': 4.0, 'x': -5.7, 'type': 'L'}, {'y1': 5.0, 'x2': -5.2, 'x1': -6.75, 'type': 'C', 'y2': 5.0}, {'y1': 2.7, 'x2': -1.6, 'x1': -2.85, 'type': 'C', 'y2': 2.7}, {'y1': 0.15, 'x2': -2.55, 'x1': -3.0, 'type': 'C', 'y2': -2.6}, {'y1': 6.85, 'x2': 0.55, 'x1': -1.7, 'type': 'C', 'y2': 8.25}, {'y1': 5.85, 'x2': 1.1, 'x1': 0.4, 'type': 'C', 'y2': 3.5}, {'y': 0.9, 'x': 0.3, 'type': 'L'}, {'y': -22.0, 'x': 9.35, 'type': 'L'}, {'y1': -3.9, 'x2': 6.55, 'x1': 1.95, 'type': 'C', 'y2': -6.25}, {'y': -5.5, 'x': 6.15, 'type': 'L'}, {'y': 3.45, 'x': -0.9, 'type': 'L'}, {'y1': 4.1, 'x2': -0.15, 'x1': -0.95, 'type': 'C', 'y2': 3.1}], [{'fr': None, 'ln': None, 'type': 'S', 'y': 83.75, 'x': 164.75, 'fl': 0}, {'y1': -4.3, 'x2': -3.15, 'x1': -0.3, 'type': 'C', 'y2': -8.35}, {'y1': -9.3, 'x2': -3.7, 'x1': -3.55, 'type': 'C', 'y2': -4.4}, {'y': -2.35, 'x': -2.25, 'type': 'L'}, {'y1': 12.05, 'x2': -1.75, 'x1': 2.7, 'type': 'C', 'y2': 4.3}, {'y1': 2.95, 'x2': -2.05, 'x1': -1.2, 'type': 'C', 'y2': 1.9}, {'y': -6.15, 'x': -3.75, 'type': 'L'}, {'y1': -5.45, 'x2': -5.6, 'x1': -3.55, 'type': 'C', 'y2': -6.15}, {'y': -5.1, 'x': -4.85, 'type': 'L'}, {'y': 9.65, 'x': 5.6, 'type': 'L'}, {'y1': 10.65, 'x2': 2.35, 'x1': 6.05, 'type': 'C', 'y2': 5.05}, {'y': 0.8, 'x': -1.85, 'type': 'L'}, {'y1': -4.9, 'x2': -2.65, 'x1': -2.85, 'type': 'C', 'y2': -2.9}, {'y': -7.65, 'x': -7.35, 'type': 'L'}, {'y': 6.9, 'x': 4.05, 'type': 'L'}, {'y1': 7.35, 'x2': 0.2, 'x1': 4.1, 'type': 'C', 'y2': 2.05}, {'y': 0.45, 'x': 0.05, 'type': 'L'}, {'y1': 1.25, 'x2': -8.9, 'x1': -5.75, 'type': 'C', 'y2': 0.05}, {'y1': -5.8, 'x2': -3.15, 'x1': -1.9, 'type': 'C', 'y2': -4.6}, {'y1': -6.35, 'x2': -7.7, 'x1': -4.3, 'type': 'C', 'y2': -9.65}, {'y1': 3.15, 'x2': 3.3, 'x1': 2.35, 'type': 'C', 'y2': 9.1}, {'y1': 8.65, 'x2': 0.95, 'x1': 3.2, 'type': 'C', 'y2': 5.25}, {'y1': -0.95, 'x2': -4.75, 'x1': -13.55, 'type': 'C', 'y2': -6.5}, {'y1': -2.3, 'x2': -1.1, 'x1': -1.7, 'type': 'C', 'y2': -3.7}, {'y': -6.05, 'x': -1.7, 'type': 'L'}, {'y': -0.65, 'x': 0.0, 'type': 'L'}, {'y': 4.1, 'x': -1.4, 'type': 'L'}, {'y1': 4.5, 'x2': -0.4, 'x1': -1.5, 'type': 'C', 'y2': 2.05}, {'y': 9.35, 'x': -1.95, 'type': 'L'}, {'y1': 4.0, 'x2': 1.15, 'x1': 1.0, 'type': 'C', 'y2': 2.6}, {'y1': 2.5, 'x2': 0.0, 'x1': 1.1, 'type': 'C', 'y2': -1.45}, {'y1': -1.85, 'x2': 0.7, 'x1': 0.0, 'type': 'C', 'y2': -8.4}, {'y': -8.05, 'x': 0.65, 'type': 'L'}, {'y': 21.0, 'x': 4.65, 'type': 'L'}, {'y': -1.1, 'x': 10.7, 'type': 'L'}, {'y1': -1.35, 'x2': 1.05, 'x1': 10.95, 'type': 'C', 'y2': -1.25}, {'y1': -1.2, 'x2': -1.75, 'x1': 1.0, 'type': 'C', 'y2': -6.95}, {'y': -5.15, 'x': -1.25, 'type': 'L'}, {'y': 13.3, 'x': 5.95, 'type': 'L'}, {'y': -1.65, 'x': 38.35, 'type': 'L'}, {'y': 0.4, 'x': 0.6, 'type': 'L'}, {'y1': -0.25, 'x2': -0.2, 'x1': 0.6, 'type': 'C', 'y2': -3.15}]])

        path3=[]
        path3.append({'fr': None, 'ln': None, 'type': 'S', 'y': 144.8, 'x': 163.05, 'fl': 0})
        path3.append({'y': -1.05, 'x': 0.85, 'type': 'L'})
        path3.append({'y1': -2.1, 'x2': 0.85, 'x1': 1.2, 'type': 'C', 'y2': -0.3})
        path3.append({'y': -5.6, 'x': 14.3, 'type': 'L'})
        path3.append({'y': -5.75, 'x': 14.5, 'type': 'L'})
        path3.append({'y': -1.0, 'x': 2.0, 'type': 'L'})
        path3.append({'y1': -0.45, 'x2': -1.2, 'x1': 0.55, 'type': 'C', 'y2': -0.5})
        path3.append({'y1': -0.4, 'x2': -5.45, 'x1': -1.05, 'type': 'C', 'y2': 2.1})
        path3.append({'y': 4.35, 'x': -11.1, 'type': 'L'})
        path3.append({'y1': 1.1, 'x2': -4.55, 'x1': -3.15, 'type': 'C', 'y2': 2.05})
        path3.append({'y1': 0.9, 'x2': -0.75, 'x1': -2.0, 'type': 'C', 'y2': -0.45})
        path3.append({'y1': -0.4, 'x2': -1.8, 'x1': -0.65, 'type': 'C', 'y2': 0.4})
        path3.append({'y': 0.5, 'x': -2.8, 'type': 'L'})
        path3.append({'fr': 1, 'ln': None, 'type': 'S', 'y': 138.2, 'x': 162.80000000000004, 'fl': None})
        path3.append({'y': 0.9, 'x': 0.4, 'type': 'L'})
        path3.append({'y1': 1.1, 'x2': -0.05, 'x1': 0.3, 'type': 'C', 'y2': 2.4})
        path3.append({'y': 2.2, 'x': -0.4, 'type': 'L'})
        path3.append({'fr': None, 'ln': None, 'type': 'S', 'y': 140.25, 'x': 60.3, 'fl': 0})
        path3.append({'y': -0.95, 'x': -0.05, 'type': 'L'})
        path3.append({'y1': -2.4, 'x2': 0.35, 'x1': 0.1, 'type': 'C', 'y2': -1.1})
        path3.append({'y': -1.3, 'x': 0.7, 'type': 'L'})
        path3.append({'fr': None, 'ln': None, 'type': 'S', 'y': 134.5, 'x': 61.400000000000006, 'fl': None})
        path3.append({'y': 134.49999999999991, 'x': 61.40000000000007, 'type': 'S'})
        path3.append({'y': -0.45, 'x': -0.35, 'type': 'L'})
        path3.append({'y1': -0.1, 'x2': -3.2, 'x1': -0.5, 'type': 'C', 'y2': -2.05})
        path3.append({'y1': -2.0, 'x2': -0.6, 'x1': -3.1, 'type': 'C', 'y2': -0.05})
        path3.append({'y1': -0.0, 'x2': 3.25, 'x1': -1.4, 'type': 'C', 'y2': 3.6})
        path3.append({'y': 3.35, 'x': 2.45, 'type': 'L'})
        path3.append({'y': 3.45, 'x': 2.35, 'type': 'L'})

        result3 = Parser.ShapeMaker._merge_path(path3)
        self.assertEqual(result3,[[{'y': 134.49999999999991, 'x': 61.40000000000007, 'type': 'S'}, {'y': -0.45, 'x': -0.35, 'type': 'L'}, {'y1': -0.1, 'x2': -3.2, 'x1': -0.5, 'type': 'C', 'y2': -2.05}, {'y1': -2.0, 'x2': -0.6, 'x1': -3.1, 'type': 'C', 'y2': -0.05}, {'y1': -0.0, 'x2': 3.25, 'x1': -1.4, 'type': 'C', 'y2': 3.6}, {'y': 3.35, 'x': 2.45, 'type': 'L'}, {'y': 3.45, 'x': 2.35, 'type': 'L'}, {'y': -0.95, 'x': -0.05, 'type': 'L'}, {'y1': -2.4, 'x2': 0.35, 'x1': 0.1, 'type': 'C', 'y2': -1.1}, {'y': -1.3, 'x': 0.7, 'type': 'L'}], [{'fr': None, 'ln': None, 'type': 'S', 'y': 144.8, 'x': 163.05, 'fl': 0}, {'y': -1.05, 'x': 0.85, 'type': 'L'}, {'y1': -2.1, 'x2': 0.85, 'x1': 1.2, 'type': 'C', 'y2': -0.3}, {'y': -5.6, 'x': 14.3, 'type': 'L'}, {'y': -5.75, 'x': 14.5, 'type': 'L'}, {'y': -1.0, 'x': 2.0, 'type': 'L'}, {'y1': -0.45, 'x2': -1.2, 'x1': 0.55, 'type': 'C', 'y2': -0.5}, {'y1': -0.4, 'x2': -5.45, 'x1': -1.05, 'type': 'C', 'y2': 2.1}, {'y': 4.35, 'x': -11.1, 'type': 'L'}, {'y1': 1.1, 'x2': -4.55, 'x1': -3.15, 'type': 'C', 'y2': 2.05}, {'y1': 0.9, 'x2': -0.75, 'x1': -2.0, 'type': 'C', 'y2': -0.45}, {'y1': -0.4, 'x2': -1.8, 'x1': -0.65, 'type': 'C', 'y2': 0.4}, {'y': 0.5, 'x': -2.8, 'type': 'L'}, {'y': 0.9, 'x': 0.4, 'type': 'L'}, {'y1': 1.1, 'x2': -0.05, 'x1': 0.3, 'type': 'C', 'y2': 2.4}, {'y': 2.2, 'x': -0.4, 'type': 'L'}]])

class TestPUtil(unittest.TestCase):

    def setUp(self):
        filename = './lightning_core/test/xmlsamples.xml'
        f = open(filename,'r')
        self.samplexml = f.read()

    def _get_xml(self, samplename, objectname):
        parser = Parser()
        xml = etree.XML(self.samplexml).xpath('.//%s/%s' % (samplename,objectname))[0]
        return xml

    def test_colortrans(self):
        # normalcolortransform
        rgba = (0, 256, 128, 100)
        ctf = {'hoge' : [100, 100, 2, 2, 200, 100, -100, 256]}
        key = 'hoge'
        self.assertEqual((200, 200, 0, 256), PUtil.colortrans(key,    rgba, ctf))
        self.assertEqual((  0, 256, 128, 100), PUtil.colortrans('huga', rgba, ctf)) # key mismatch

    def test_colortrans_only_alpha(self):
        # gradientTransform
        ctf = {'hoge' : [0, 0, 0, 100, 0, 0, 0, 56]}
        self.assertEqual(156.0, PUtil.colortrans_only_alpha('hoge', ctf))
        self.assertEqual(0.0,   PUtil.colortrans_only_alpha('fuga', ctf)) # key mismatch

    def test__get_pixel_vals(self):
        self.assertAlmostEqual(PUtil.get_pixel_vals(200), 10)
        vals = PUtil.get_pixel_vals(200,300,400)
        self.assertAlmostEqual(vals[0], 10)
        self.assertAlmostEqual(vals[1], 15)
        self.assertAlmostEqual(vals[2], 20)
        self.assertAlmostEqual(len(PUtil.get_pixel_vals(200,None, 400)), 3)
        vals = PUtil.get_pixel_vals(200,0,400)
        self.assertAlmostEqual(vals[0], 10)
        self.assertAlmostEqual(vals[1], 0)
        self.assertAlmostEqual(vals[2], 20)
        vals = PUtil.get_pixel_vals(200,None,400)
        self.assertAlmostEqual(vals[0], 10)
        self.assertEqual(vals[1], None)
        self.assertAlmostEqual(vals[2], 20)

    def test__convert_color_as_tuple(self):
        elm1 = {'red':100, 'green':0, 'blue':256}
        self.assertEqual(PUtil.convert_color_as_tuple(elm1), (100,0,256,256))
        elm1 = {'red':10, 'green':0, 'blue':255, 'alpha': 222}
        self.assertEqual(PUtil.convert_color_as_tuple(elm1), (10,0,255,222))


if __name__ == '__main__':
    unittest.main()

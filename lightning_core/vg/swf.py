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

import hashlib
from vg import Transform, Rect
from lightningutil import LUtil

class Place(Transform):
    def __init__(self, t, ct, objectId, depth, name, clipDepth):
        super(Place, self).__init__()

        self.id = objectId
        self.depth = depth
        self.swf_depth = 1
        self.clipDepth = clipDepth 
        self.name = name
        self.visible = True
        self.symbols = []

        self.sx = None
        self.sy = None
        self.wx = None
        self.wy = None
        self.tx = None
        self.ty = None

        if len(t) > 0:
            self.sx,self.sy,self.wx,self.wy,self.tx,self.ty=tuple(LUtil.get_values_as_float(t[0],'scaleX','scaleY','skewX','skewY','transX','transY'))

        self.ctf = []

        if len(ct) > 0:
            factors = LUtil.get_colortrans(ct[0], 'factor')
            offsets = LUtil.get_colortrans(ct[0], 'offset')

            self.ctf = factors + offsets

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, val):
        self.__dict__[key] = val

    def items(self):
        return self.__dict__



class Frame(object):
    def __init__(self):
        self.places = []

    def addPlace(self, matrixAndPlaceDict, symbols, name=None, visible=True):
        place = Place([], [], None, None, name, None)
        attr = {'visible': visible,
                'symbols': symbols}
        attr.update(matrixAndPlaceDict)
        # convert swf_depth and depth
        attr['swf_depth'] = attr['depth']
        attr['depth'] = 1
        if name is not None:
            attr['name'] = name
        place.set_items(attr)
        # self.places.append(attr)
        self.places.append(place)

        self._reassignDepth()

    def _reassignDepth(self):
        self.places.sort(lambda x, y: cmp(x['swf_depth'], y['swf_depth']))

        index = 1
        for p in self.places:
            # p['depth'] = index
            p['depth'] = p['swf_depth']
            index += 1

    def __len__(self):
        return len(self.places)


class Sprite(object):

    def __init__(self):
        self.symbol = ""
        self.frames = []

    def addFrame(self, frame):
        self.frames.append(frame)

    def searchSymbols(self, depth):
        result = []

        for f in self.frames:
            for p in f.places:
                if p['swf_depth'] == depth:
                    for s in p['symbols']:
                        if s not in result:
                            result.append(s)
        return result

    def __len__(self):
        return len(self.frames)

class Edge(object):

    def __init__(self):
        self.colors = []
        self.values = []
        self.lineWidths = []

    def add(self, val):
        self.values.append(val)

    def add_colors(self, category, colors):
        self.colors = self.colors + map(lambda ar: {category:ar},colors)

    def add_line(self, widths):
        self.lineWidths = self.lineWidths + widths

    def get_colors_from_category(self, category):
        result = []
        for c in self.colors:
            if c.keys()[0] == category:
                result.append(c)
        return result
                

    def get_path(self, index, style):
        result = []

        contain = False

        if style == 'left':
            key = 'fl'
        elif style == 'right':
            key = 'fr'
        elif style == 'line':
            key = 'ln'

        for v in self.values:
            if v['type'] == 'S':
                if v[key] is not None:
                    if v[key] == index:
                        contain = True
                    else:
                        contain = False

            if contain:
                    result.append(v)

        return result


class Shape(Rect):
    def __init__(self):
        super(Shape, self).__init__()
        self.symbol = ""
        self.name = ""
        self.edges = []
        self.defs = []
        # self.offsetX = 0
        # self.offsetY = 0
        # self.color = (0, 0, 0)
        # self.paths = []

    def append(self, edge):
        #if edge not in self.edges:
        self.edges.append(edge)

    def generate_name(self):
        m = hashlib.sha1()
        m.update(self.symbol)
        # dump = [json.dumps(e) for p in self.edges for e in p.values]
        # m.update(''.join(str(i) for i in dump))
        return m.hexdigest()




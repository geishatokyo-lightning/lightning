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

from lightningutil import LUtil
from lxml import etree

class Rect(object):
    def __init__(self):
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0

    def get_width(self):
        return self.right - self.left
    def set_width(self, v):
        'deprecated'
        pass
    width = property(get_width, set_width)

    def get_height(self):
        return self.bottom - self.top
    def set_height(self, v):
        'deprecated'
        pass
    height = property(get_height, set_height)

class Color(list):
    def __init__(self, args):
        if len(args) == 3:
            args.append(256)
        if len(args) == 4:
            super(Color, self).__init__(args)

    def _get_element(self, index):
        if len(self) >= 3:
            return self[index]
        return None

    def _get_r(self):
        return self._get_element(0)

    def _get_g(self):
        return self._get_element(1)

    def _get_b(self):
        return self._get_element(2)

    def _get_a(self):
        return self._get_element(3)

    def get_rgb(self):
        if len(self) >= 3:
            return ('#%02x%02x%02x' % (self._get_r(), self._get_g(), self._get_b())).lower()
        return None

    def transform(self, ctf):
        if len(ctf) == 8:
            for i, v in enumerate(self):
                m = 255
                if i == 3:
                    m = 256
                self[i] = max(0, min(int(v * ctf.factor[i]/256) + ctf.offset[i], m))
        return self

    def get_colors(self):
        return (self._get_r(), self._get_g(), self._get_b(), self._get_a())

    r = property(_get_r)
    g = property(_get_g)
    b = property(_get_b)
    a = property(_get_a)

class ColorTransform(list):
    def __init__(self, args):
        self.factor = None
        self.offset = None
        if len(args) == 8:
            self.factor = Color(args[:4])
            self.offset = Color(args[4:])
        super(ColorTransform, self).__init__(args)

class Path(etree.ElementBase):
    def __init__(self, category=None, attrib=None, nsmap=None,  **_extra):
        super(Path, self).__init__(attrib=None, nsmap=None, **_extra)
        self.tag = 'path'
        self.set('clip-rule', 'evenodd')
        if category == 'line':
            self.set('stroke-opacity','undefined')
            self.set('fill', 'none')

class LinearGradient(etree.ElementBase):
    def __init__(self, objectId, gtf, stops, attrib=None, nsmap=None,  **_extra):
        super(LinearGradient, self).__init__(attrib=None, nsmap=None, **_extra)
        self.tag = 'linearGradient'
        self.set('gradientUnits', 'userSpaceOnUse')
        # why 16384/20, see swf specification
        self.set('x1', '-819')
        self.set('x2',  '819')
        self.set('id', objectId)
        self.set('gradientTransform', 'matrix(%.2f %.2f %.2f %.2f %.4f %.4f)' % self._make_gradient(gtf))
        for stop in stops:
            self.append(stop)

    def _make_gradient(self, gtf):
        transform = Transform()
        transform.set_items(dict(zip(transform.MATRIX, LUtil.get_transform_matrix(gtf))))
        return transform.get_matrix()


class Stop(etree.ElementBase):
    def __init__(self, clr, position, attrib=None, nsmap=None,  **_extra):
        super(Stop, self).__init__(attrib=None, nsmap=None, **_extra)
        self.tag = 'stop'
        self.set('stop-color'  , LUtil.rgb_to_hex(clr))
        self.set('stop-opacity', str(float(clr[3]/255)))
        self.set('offset'      , str(float(position)/255))


class Transform(dict):
    MATRIX = ('sx','wx','wy','sy','tx','ty')
    def __init__(self):
        super(Transform, self).__init__()
        self.sx = 1.0
        self.sy = 1.0
        self.wx = 0.0
        self.wy = 0.0
        self.tx = 0.0
        self.ty = 0.0
        self.ctf = []
        self.depth = 1
        self.clipDepth = None
        self.name = None
        self.visible = True

    def set_items(self, attrib):
        for k, v in attrib.iteritems():
            if k in self.__dict__ and v is not None:
                self.__dict__[k] = v

    def get_matrix(self):
        return self.sx, self.wx, self.wy, self.sy, self.tx/20, self.ty/20

class Tree(Transform):

    def __init__(self):
        super(Tree, self).__init__()
        self.key = None
        self.children = []
        self.parent = None

    def __str__(self):

        result = "key=%s" % self.key

        result_children = ""
        for c in self.children:
            for line in str(c).split('\n'):
                if len(line) > 0:
                    result_children += '\t' + line + '\n'

        result += '\n' + result_children[:-1]

        return result

class AnimFrame(Transform):
    def __init__(self):
        super(AnimFrame, self).__init__()
        self.index = 0

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, val):
        self.__dict__[key] = val

class Animation(object):

    def __init__(self):

        self.key = None
        self.frames = []

    def appendFrame(self, index, sx, sy, wx, wy, tx, ty, ctf, visible=True):
        frame = AnimFrame()
        frame.set_items({'index': index,
                            'sx': sx, 'sy': sy,
                            'wx': wx, 'wy': wy,
                            'tx': tx, 'ty': ty,
                            'ctf': ctf, 'visible':visible})
        self.frames.append(frame)

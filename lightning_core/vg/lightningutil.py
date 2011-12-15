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

KEY_SPLITTER = '-'
class LUtil(object):
                    
    @staticmethod
    def get_values(elm, *keys):
        return [elm.get(k) for k in keys]

    @staticmethod
    def get_values_as_float(elm, *keys):
        values = [elm.get(k) for k in keys]
        return [float(v) if v is not None else None for v in values]

    @staticmethod
    def get_values_as_int(elm, *keys):
        values = [elm.get(k) for k in keys]
        return [int(v) if v is not None else None for v in values]

    @staticmethod
    def get_colortrans(color, style=None):
        colorSet = ('red','green','blue','alpha')
        if style is not None:
            colorArray = [style + clr.capitalize() for clr in colorSet]
            colorSet = tuple(colorArray)

        red, green, blue, alpha = LUtil.get_values_as_int(color,colorSet[0],colorSet[1],colorSet[2],colorSet[3])

        default = 256 if style == 'factor' else 0 
        f = lambda c: c if c is not None else default
        return map(f,(red, green, blue, alpha))

    @staticmethod
    def rgb_to_hex(rgba):
        return '#%02x%02x%02x' % tuple([max(0,min(255, c)) for c in rgba[0:3]])

    @staticmethod
    def get_transform_matrix(elm):
        return LUtil.get_values_as_float(elm,'scaleX','skewX','skewY','scaleY','transX','transY')

    @staticmethod
    def make_key_string(objectID, prefix='', suffix='', splitter=KEY_SPLITTER):
        return splitter.join([prefix, objectID, suffix])

    @staticmethod
    def objectID_from_key(key, splitter=KEY_SPLITTER):
        elem = key.split(splitter)
        if len(elem) > 1:
            return elem[1]
        return key

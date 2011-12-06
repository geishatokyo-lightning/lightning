#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    def get_ctf(color, style=None):
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

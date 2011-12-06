# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
import sys
from lxml import etree
from copy import deepcopy
from parser import *
from StringIO import StringIO
import logging
import simplejson as json
import re
from collections import deque
from copy import deepcopy

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

class CssElement(dict):

    def __init__(self, title=''):
        super(CssElement, self).__init__()

        self.common_element = {
            'position' : ['position', 'absolute'],
            'transform': ['-webkit-transform', None],
            'origin'   : ['-webkit-transform-origin', '0.0px 0.0px'],
        }
        self.animation_element = {
            'name'     : ['-webkit-animation-name', None],
            'timing'   : ['-webkit-animation-timing-function', 'linear'],
            'count'    : ['-webkit-animation-iteration-count', 'infinite'],
            'duration' : ['-webkit-animation-duration', None],
        }
        self.shape_element = {
            'left'   : ['left'   , None],
            'top'    : ['top'    , None],
            'width'  : ['width'  , None],
            'height' : ['height' , None],
        }

        self.title = title
        self.sp = '\n' # splitter

    def __str__(self):
        content = self.sp.join(['%s: %s;' % (k,v) for k,v in self.iteritems()])
        return '%s {%s%s%s}%s' % (self.title, self.sp, content, self.sp, self.sp)

    def add_anims_element(self, key, anim_length, has_anim_name):
        self.animation_element['name'][1]      = key
        self.animation_element['duration'][1]  = '%fs'%(float(anim_length)/12.0)
        if not has_anim_name:
            del self.animation_element['name']
        self.update(self.animation_element.values())
        self.update(self.common_element.values())

    def add_shape_element(self, shape_key, shape_table):
        def calc_twips_to_pixel(twips):
            return '%dpx' % int(round(float(twips)/20))

        shape  = shape_table[shape_key]
        self.shape_element['left'][1]   = calc_twips_to_pixel(shape.left)
        self.shape_element['top'][1]    = calc_twips_to_pixel(shape.top)
        self.shape_element['width'][1]  = calc_twips_to_pixel(shape.width)
        self.shape_element['height'][1] = calc_twips_to_pixel(shape.height)
        self.update(self.shape_element.values())

        del self.common_element['origin']

    def add_origin_element(self, matrix):
        self.common_element['transform'][1] = matrix
        self.update(self.common_element.values())

class SvgShape(object):
    def __init__(self, elem):
        self.obj = elem[0]
        self.hash = elem[1]
        self.left = int(elem[2])
        self.top = int(elem[3])
        self.width = int(elem[4])
        self.height = int(elem[5])
        self.symbol = ''
        self.edges = []
        self.defs  =[]

    def filename(self, dir_path='.'):
        return os.path.join(dir_path, '%s_%s.svg' % (self.obj, self.hash))

class SvgTransform(Transform):
    def __init__(self, attrib):
        super(SvgTransform,self).__init__()
        values = dict([(k,float(attrib[k])) if k in attrib else (k,None) for k in self.MATRIX])
        self.set_items(values)

        if 'depth' in attrib:
            self.depth = int(attrib['depth'])
        if 'ctf' in attrib:
            self.ctf = ColorTransform([int(ctf.strip()) for ctf in attrib['ctf'].strip('[]').split(',') if ctf.strip().lstrip('-').isdigit()])
        if 'clipDepth' in attrib:
            self.clipDepth = int(attrib['clipDepth'])
        if 'visible' in attrib and attrib['visible'] == 'False':
            self.visible = False

    def __eq__(self, other):
        return [self.sx, self.sy, self.wx, self.wy, self.tx, self.ty, self.get_opacity()]==other

    def write_matrix(self):
        return self._shorten('matrix(%.6f,%.6f,%.6f,%.6f,%.6f,%.6f)' % self.get_matrix())

    def write_matrix3d(self):
        return self._shorten('matrix3d(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,%.6f,%.6f,0,1)' % (self.sx, self.wx, self.wy, self.sy, self.tx/20, self.ty/20))

    def write_webkit_transform(self):
        return self._shorten('-webkit-transform: %s;' % self.write_matrix3d())

    def _shorten(self, str):
        return str.replace('.000000', '.0')

    def get_opacity(self):
        opacity = 1.0
        if not self.visible:
            opacity = 0.0
        else:
            if len(self.ctf) == 8:
                c = Color([0,0,0,256])
                c.transform(self.ctf)
                opacity = (float(c.a) / 256.0)
        return opacity
        
    def write_visible(self):
        return self._shorten('opacity: %.6f;' % self.get_opacity())

class AnimationManager(object):
    def __init__(self, dir_path, basefilename):
        self.dir_path = dir_path
        self.shapes_filepath = self._get_path('shapes')
        self.animation_filepath = self._get_path('animation.xml')
        self.structure_filepath = self._get_path('structure.xml')
        self.cssfilepath = os.path.join('.', basefilename + '.css')
        self.htmlfilepath = os.path.join('.', basefilename + '.html')
        self.xmlfilename = os.path.basename(basefilename.replace('.svg',''));

    def _get_path(self, filename):
        return os.path.join(self.dir_path, filename)

    def load_shapes(self):
        with open(self.shapes_filepath, 'r') as f:
            return self.get_shapes(f.readlines())

    def get_shapes(self, lines):
        shape_table = {}
        for line in lines:
            elems = line.split(' ')
            if len(elems) == 6: # 'shapes'
                shape_table[elems[0]] = SvgShape(elems)
        return shape_table

    def load_animation(self):
        root = self._parse_xml(self.animation_filepath)
        return self.get_animation(root)

    def get_animation(self, root):
        anim_table = {}
        for anim in root.xpath('//animation'):
            key = anim.attrib['key']
            frames = anim.findall('frame')
            anim_table[key] = [SvgTransform(frame.attrib) for frame in frames]
        return anim_table

    def load_structure(self, shape_table, parser_shapes):
        root = self._parse_xml(self.structure_filepath)
        return self.get_structure(root, shape_table, parser_shapes)

    def get_structure(self, root, shape_table, anim_table, ctfsArray, parser_shapes, mcname=None, key_prefix=""):
        def get_parent_key(elem):
            parent = elem.getparent()
            if parent is not None and parent.attrib.has_key('class'):
                p_attrib_cls = parent.attrib['class']
                s = re.search('obj\d+', p_attrib_cls)
                if s is not None:
                    return s.group()
            else:
                return ''

        def update_elem(elem, key, name, hasClipDepth):
            elem.tag = 'div'
            elem.attrib.clear()
            elem.attrib['class'] = key
            if name is not None :
                elem.attrib['id'] = name
            if hasClipDepth:
                elem.attrib['style'] = 'display:none;'


        structure_table = {}
        
        if mcname is None:
            root_elem = root
        else:
            r = root.xpath('//part[@name="%s"]'%mcname)
            if r is None:
                root_elem = root
            else:
                root_elem = r[0]
        for elem in root.xpath('//part'):
            if 'key' in elem.attrib:
                key          = elem.attrib['key']
                objId        = LUtil.objectID_from_key(key)
                depth        = elem.attrib['depth']
                hasClipDepth = 'clipDepth' in elem.attrib
                name         = elem.attrib['name'] if 'name' in elem.attrib else None
                ctf          = json.loads(elem.attrib['ctf'])

                if len(ctf) > 1:
                    ctfsArray.append({key:ctf})

                key_depth = LUtil.make_key_string(key, prefix=key_prefix, suffix=depth)

                structure_table[key_depth] = SvgTransform(elem.attrib)

                update_elem(elem, key_depth, name, hasClipDepth)

                k = objId[3:]
                if (len(elem) == 0) and (k in parser_shapes):
                    shape_key  = LUtil.make_key_string(objId, prefix=key_prefix, suffix='shape')
                    parent_key = get_parent_key(elem)

                    childdiv = etree.Element('div')
                    childdiv.set('class', shape_key)

                    structure_table[shape_key] = SvgTransform(childdiv.attrib)

                    svgelem  = Parser.str_shape_as_svg(parser_shapes[k], ctfsArray, parent_key)
                    childdiv.append(svgelem)
                    elem.append(childdiv)

        structure_tree = deepcopy(root_elem)
        return structure_table, structure_tree

    def _parse_xml(self, filepath):
        with open(filepath, 'r') as f:
            return etree.parse(f)
        return None

    def _remove_deplicated_keyframes(self, anim_elements):
        anim_buffer = deque()
        result = []
        for percent, transform in anim_elements:
            anim_buffer.append((percent, transform))
            if len(anim_buffer) == 3:
                if anim_buffer[0][1] == anim_buffer[1][1] and anim_buffer[0][1] == anim_buffer[2][1]:
                    anim_buffer = deque((anim_buffer[0], anim_buffer[2]))
                else:
                    result.append(anim_buffer.popleft())

        result.extend(list(anim_buffer))
        return result

    def _interpolate_keyframes(self, anim_elements, eps=0.0001):
        result = []
        old_transform = None
        for i, (percent, transform) in enumerate(anim_elements):
            if old_transform is not None:
                if (not old_transform.visible and transform.visible):
                    temp_transform = deepcopy(transform)
                    temp_transform.visible = old_transform.visible
                    result.append((percent - eps, temp_transform))
                elif (old_transform.visible and not transform.visible):
                    result.append((percent - eps, old_transform))
            result.append((percent, transform))
            old_transform = transform
        if len(result) > 0:
            result.append((100.0, result[0][1])) # 100% animation
        return result

    def _make_keyframes(self, anim_table, key_prefix='', sp='\n'):
        keyframes = []
        for key, value in anim_table.iteritems():
            anim_length = len(value)
            anim_elements = [((float(i*100)/float(anim_length)), a) for i,a in enumerate(value)]
            anim_list = ['%f%% { %s %s }' % (percent, a.write_webkit_transform(), a.write_visible()) for percent, a in self._interpolate_keyframes(self._remove_deplicated_keyframes(anim_elements))]
            anim = sp.join(anim_list)
            keyframes.append(sp.join(['@-webkit-keyframes %s {'%(key), anim, '}']))
        return (sp+sp).join(keyframes)

    def _make_transform(self, structure_table, shape_table, anim_table, key_prefix='', has_anim_name=True, sp='\n'):

        result = []
        for key, structure in structure_table.iteritems():
            elem = CssElement(title='.%s'%key)
            transform = ('-webkit-transform', structure.write_matrix())

            if key in anim_table:
                anim_length = len(anim_table[key])
                elem.add_anims_element(key, anim_length, has_anim_name)

            shape_key = LUtil.objectID_from_key(key)
            if key.endswith('shape') and shape_key in shape_table:
                elem.add_shape_element(shape_key, shape_table)

            elem.add_origin_element(structure.write_matrix())
            result.append(str(elem))

        return (sp+sp).join(result)

    def write_html(self, structure_tree, cssfilepath):
        template = '''<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="ja" xml:lang="ja">
  <head>
    <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8"></meta>
    <link href="%s" type="text/css" rel="stylesheet"></link>
    <title>lightning</title>
  </head>
  <body>
%s
  </body>
</html>
'''
        html = template % (cssfilepath, etree.tostring(structure_tree, pretty_print=True))
        return html

    def write_div(self, structure_tree):
        html = "%s" % (etree.tostring(structure_tree, pretty_print=True))
        return html

    def write_css(self, structure_table, shape_table, anim_table, key_prefix='', has_anim_name=True, sp='\n\n'):
        elem = CssElement(title='div')
        css = sp.join([self._make_keyframes(anim_table, key_prefix), self._make_transform(structure_table, shape_table, anim_table, key_prefix, has_anim_name)])
        return 'svg { display:block; }\n' + css

    def _write(self, filepath, content):
        with open(filepath, 'w') as f:
            f.write(content)



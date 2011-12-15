#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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

from __future__ import with_statement
import sys
import os
import os.path
import re
import copy

from lightningutil import LUtil
from swf import *

try:
    from lxml import etree
except:
    print "lxml package is required"
    sys.exit()

from vg import *
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

class SvgBuilder(object):

    def __init__(self, xmlfile, key_prefix='', scale_factor=1.0):
        self.parser = Parser()
        self.parser.parse(xmlfile, key_prefix, scale_factor=scale_factor)

    def get_shapes_as_dict(self):
        return self.parser.shapes

    def get_shapes(self):
        buf = ""
        buf += "%d\n" % len(self.parser.shapes)
        for k, v in self.parser.shapes.iteritems():
            buf += "%s %s %d %d %d %d\n" % (v.symbol,
                                            v.name,
                                            v.left, v.top,
                                            v.width, v.height)

        return buf

    def get_animation(self):
        return self.parser.str_animation()

    def get_structure(self):
        structure = etree.Element("structure")

        self.parser.add_tree(self.parser.tree, structure)
        return structure

    #----save-----
    def save_as_static_svg(self, output_path):
        # self._save_svg(outdirname)
        name, svgstr = self.parser.make_svg()
        with open(output_path, 'w') as fp:
            fp.write(svgstr)

    def save(self, outdirname):

        if not os.path.exists(outdirname):
            os.makedirs(outdirname)

        self._save_svgs(outdirname)
        self._save_shapes(outdirname)
        self._save_structure(outdirname)
        self._save_animation(outdirname)

    def _save_svgs(self, outdirname):
        # save shapes as svg files
        for k, v in self.parser.shapes.iteritems():
            svg_path = os.path.join(outdirname, "obj%s_%s.svg" % (k, v.name))
            Parser.save_shape_as_svg(v, [], svg_path)
            logging.debug("Converted to %s" % svg_path)

    def _save_svg(self, outdirname):

        if not os.path.exists(outdirname):
            os.makedirs(outdirname)

        name, svgstr = self.parser.make_svg()

        filepath = os.path.join(outdirname, name + ".svg")

        with open(filepath, "w") as fp:
            fp.write(svgstr)


    def _save_shapes(self, outdirname):
        shapes_path = os.path.join(outdirname, "shapes")
        with open(shapes_path, "w") as fp:
            fp.write(self.get_shapes())
        logging.debug("Converted to %s" % shapes_path)

    def _save_structure(self, outdirname):
        structure_path = os.path.join(outdirname, "structure.xml")
        with open(structure_path, "w") as fp:
            fp.write(etree.tostring(self.get_structure(), pretty_print=True))
        logging.debug("Converted to " + structure_path)

    def _save_animation(self, outdirname):
        animations_path = os.path.join(outdirname, "animation.xml")
        with open(animations_path, "w") as fp:
            fp.write(etree.tostring(self.get_animation(), pretty_print=True))
        logging.debug("Converted to " + animations_path)

class Parser(object):

    NAMESPACES = {None: "http://www.w3.org/2000/svg",
                  'xlink': "http://www.w3.org/1999/xlink"}

    XLINK = "{%s}" % NAMESPACES['xlink']

    MATRIX_KEY = ('sx', 'wx', 'wy', 'sy', 'tx', 'ty')
    PLACE_KEY  = ('ctf', 'depth', 'clipDepth')

    def __init__(self):
        self.shapes = {}
        self.sprites = {}
        self.places = {}

        self.tree = None
        logging.debug('log test: parser initialized')

    def _search_shape(self, key):
        objID = str(key[3:])

        if objID in self.shapes.keys():
            return self.shapes[objID]
        else:
            return None

    def _search_sprite(self, key):
        objID = str(key[3:])

        if objID in self.sprites.keys():
            return self.sprites[objID]
        else:
            return None

# defineshape methods
    def _get_styles_colors(self, colorElms, shape, num):
        colors = []
        for style in colorElms:
            for i in range(len(style)):
                if len(style[i].xpath('color/Color')) > 0:
                    c = PUtil.convert_color_as_tuple(style[i].xpath('color/Color')[0])
                    colors.append(c)
                elif len(style[i]) > 0:
                    gradElm = style[i]
                    objectId = "%s_%d" % (shape.symbol, num)
                    gradient = self._get_styles_gradient(gradElm, objectId)
                    shape.defs.append(gradient)
                    c = "url(#%s_%d)" % (shape.symbol, num)
                    colors.append(c)
                    num = num + 1
        return colors

    def _get_styles_lines(self, lineElms):
        colors = []
        widths = []
        for lineElm in lineElms:
            colorElms =  lineElm.xpath('color/Color')
            lineWidth = lineElm.get('width')
            if len(colorElms) > 0:
                c = PUtil.convert_color_as_tuple(colorElms[0])
                w = PUtil.get_pixel_vals(lineWidth)
                colors.append(c)
                widths.append(w)
        return colors, widths

    def _get_styles_gradient(self, e, objectId):
        stops = []
        gclr = e.find('gradientColors')
        for gc in list(gclr):
            position = gc.get('position')
            c = gc.find('color/Color')
            color = LUtil.get_colortrans(c)
            stop = Stop(color, position)
            stops.append(stop)

        gtf = e.find('matrix/Transform')
        linearGrad = LinearGradient(objectId, gtf, stops)

        return linearGrad

    def _proc_define_shape(self, e):

        objectID = e.get("objectID")
        if objectID is None:
            return

        shape = Shape()
        shape.symbol = "obj" + objectID

        # width and height
        rect = e.xpath("./bounds/Rectangle")[0]

        shape.left   = float(rect.get('left'))
        shape.right  = float(rect.get('right'))
        shape.top    = float(rect.get('top'))
        shape.bottom = float(rect.get('bottom'))

        shape.width  = shape.get_width()
        shape.height = shape.get_height()

        num = 0

        ### styles ###
        # color
        colorElms = e.xpath("./styles/StyleList/fillStyles")
        lineElms = e.xpath("./styles/StyleList/lineStyles/LineStyle")

        edge = Edge()

        if len(colorElms) > 0:
            solidcolors = self._get_styles_colors(colorElms, shape, num)
            if len(solidcolors) > 0:
                edge.add_colors('s', solidcolors)
        #lineStyles
        if len(lineElms) > 0:
            linecolors, widths = self._get_styles_lines(lineElms)
            if len(linecolors) > 0:
                edge.add_colors('l',linecolors)
                edge.add_line(widths)

        if len(colorElms) > 0 or len(lineElms) > 0:
                shape.append(edge)

        ### shapes ###
        edgeElms = e.xpath("./shapes/Shape/edges")

        cx = cy = 0

        for elm in edgeElms:

            methods = elm.xpath("./*")

            for m in methods:

                if m.tag == "ShapeSetup":
                    x, y = PUtil.get_pixel_vals(m.get('x'), m.get('y'))

                    fillStyle0 = m.get("fillStyle0")
                    fillStyle1 = m.get("fillStyle1")
                    lineStyle = m.get("lineStyle")

                    nextColorElms = m.xpath("./styles/StyleList/fillStyles")
                    nextLineElms = m.xpath("./styles/StyleList/lineStyles/LineStyle")

                    if len(nextColorElms) > 0 or len(nextLineElms) > 0:
                        edge = Edge()

                    # solid color or gradient
                    if len(nextColorElms) > 0:
                        colors = self._get_styles_colors(nextColorElms, shape, num)
                        if len(colors) > 0:
                            edge.add_colors('s', colors)
                            shape.append(edge)
                    else:
                        fillLeft , fillRight , lineCenter = map(lambda x: x and int(x) - 1, [fillStyle0, fillStyle1, lineStyle])
                        if x is not None and y is not None:
                            cx = x
                            cy = y

                        if not set([x, y]) == set([None]):
                            edge.add({'type': 'S',
                                      'x': x, 'y': y,
                                      'fl': fillLeft, 'fr': fillRight, 'ln': lineCenter})
                        else:
                            edge.add({'type': 'S',
                                      'x': cx, 'y': cy,
                                      'fl': fillLeft, 'fr': fillRight, 'ln': lineCenter})
                    # lineStyles
                    if len(nextLineElms) > 0:
                        colors, widths = self._get_styles_lines(nextLineElms)
                        if len(colors) > 0:
                            edge.add_colors('l',colors)
                            edge.add_line(widths)
                            shape.append(edge)


                if m.tag == "LineTo" and edge is not None:
                    x, y = PUtil.get_pixel_vals(m.get('x'), m.get('y'))

                    if x is not None and y is not None:
                        cx += x
                        cy += y
                        edge.add({'type': 'L',
                                  'x': x, 'y': y})

                if m.tag == "CurveTo" and edge is not None:
                    x1, y1, x2, y2 = PUtil.get_pixel_vals(m.get("x1"), m.get("y1"), m.get("x2"), m.get("y2")) 
                    if not set([x1, x2, y1, y2]) == set([None]):
                        cx += x1 + x2
                        cy += y1 + y2
                        edge.add({'type': 'C',
                                  'x1': x1,
                                  'y1': y1,
                                  'x2': x2,
                                  'y2': y2})

        self.shapes[objectID] = shape

    def _proc_define_sprite(self, e, key_prefix=''):
        objectID = e.get("objectID")
        if objectID is None:
            return

        sprite = Sprite()
        sprite.symbol = "obj" + objectID

        has_do_action = False

        depth_table = {}
        po_table = {}

        frame_list = [] 
        fr = {}
        for p in e.xpath("./tags/*"):
            if p.tag == "DoAction":
                has_do_action = True
                break
            elif p.tag == "PlaceObject2":
                depth = int(p.get('depth'))
                placeObjectID = p.get("objectID")
                if not depth in depth_table:
                    depth_table[depth] = placeObjectID
                    po_table[depth] = self._get_place_object(p)

                fr[depth] = True
            elif p.tag == "RemoveObject2":
                depth = int(p.get('depth'))
                fr[depth] = False
            elif p.tag == "ShowFrame":
                for depth in depth_table.iterkeys():
                    if not depth in fr:
                        fr[depth] = frame_list[-1][depth]

                frame_list.append(fr)
                fr = {}
        for i, f in enumerate(frame_list):
            if len(f) < len(depth_table):
                pids = [(depth, False) for depth in depth_table.iterkeys() if not depth in f]
                frame_list[i].update(pids)

        frame = Frame()
        for p in e.xpath("./tags/*"):
            if p.tag == "PlaceObject2":

                po = self._get_place_object(p)

                depth = po['depth']
                placeObjectID = po["id"]

                if placeObjectID is not None:
                    symbols = [LUtil.make_key_string("obj" + placeObjectID, prefix=key_prefix, suffix='%d'%depth)]
                else:
                    symbols = sprite.searchSymbols(depth)

                poMatrixArray = [po[key] for key in self.MATRIX_KEY]
                if set(poMatrixArray) == set([None]):
                    logging.debug('including only ColorTransform animation')
                    places = [place for place in sprite.frames[-1].places if place.depth == depth]
                    if len(places) > 0:
                        p_temp = places[0]
                        po.items().update(dict((k, p_temp[k]) for k in self.MATRIX_KEY if p_temp[k] is not None))
                frame.addPlace(dict((k, po[k]) for k in self.MATRIX_KEY+self.PLACE_KEY), symbols, po['name'])

            elif p.tag == "ShowFrame":
                depth_list = [place.depth for place in frame.places]
                for depth, placeObjectID in depth_table.iteritems():
                    if not depth in depth_list and not frame_list[len(sprite.frames)][depth]:
                        symbols = [LUtil.make_key_string("obj" + placeObjectID, prefix=key_prefix, suffix='%d'%depth)]
                        po = po_table[depth]
                        frame.addPlace(dict((k, po[k]) for k in self.MATRIX_KEY+self.PLACE_KEY), symbols, None, frame_list[len(sprite.frames)][depth])
                sprite.addFrame(frame)
                frame = Frame()
                # doaction is not implemented
                if has_do_action:
                    break

        self.sprites[objectID] = sprite

    def _get_place_object(self, e, depth=None):
        t = e.xpath('./transform/Transform')
        ct = e.xpath('./colorTransform/ColorTransform2')

        if depth is None and e.get('depth') is not None:
            depth = int(e.get('depth'))
        clipDepth = e.get('clipDepth')
        name = e.get('name', None)
        placeObjectID = e.get("objectID")

        place = Place(t, ct, placeObjectID, depth, name, clipDepth)
        return place

    def _proc_place_object(self, e):
        placeObjectID = e.get("objectID")
        self.places[placeObjectID] = self._get_place_object(e)

    def parse_from_str(self, filestr):
        tree = etree.fromstring(filestr)
        self.__parse(tree)

    def parse(self, xmlfile, key_prefix='', scale_factor=1.0):
        tree = etree.parse(xmlfile, parser=etree.XMLParser())
        self.__parse(tree, key_prefix, scale_factor)
        if xmlfile is not None:
            xmlfile.close()

    def __parse(self, tree, key_prefix='', scale_factor=1.0):
        self.size = tree.xpath("//swf/Header/size/Rectangle")

        elms = tree.xpath("//swf/Header/tags/*")

        defineRe = re.compile('DefineShape[2-5]?')
        for e in elms:
            if defineRe.match(e.tag) is not None:
                self._proc_define_shape(e)

            if e.tag == 'DefineSprite':
                self._proc_define_sprite(e, key_prefix)

            if e.tag == "PlaceObject2":
                self._proc_place_object(e)
        for k, v in self.shapes.iteritems():
            v.name = v.generate_name()

        self._build_tree(scale_factor)

    def make_svg(self):

        def pick_tree(tree, key):
            result = []

            if tree.key == key:
                result.append(tree)

            for c in tree.children:
                result.extend(pick_tree(c, key))

            return result

        def get_rect(key, absolute=True):

            trees = pick_tree(self.tree, key)

            left = 1e10
            top = 1e10
            right = -1e10
            bottom = -1e10

            for tr in trees:
                if len(tr.children) == 0:
                    shape = self._search_shape(tr.key)

                    l = shape.left
                    t = shape.top
                    w = shape.width
                    h = shape.height

                    l += tr.tx
                    t += tr.ty

                    curr = tr.parent

                    while curr is not None:

                        parent = curr.parent

                        if parent is not None:

                            if(absolute or
                               parent.key != 'root'):
                                # TODO compute rect with scale and skew
                                # (e.g. sx, sy, wx, and wy)
                                l += curr.tx
                                t += curr.ty

                        curr = parent

                    if left > l:
                        left = l

                    if right < l + w:
                        right = l + w

                    if top > t:
                        top = t

                    if bottom < t + h:
                        bottom = t + h

            width = right - left
            height = bottom - top

            if width < 0 or height < 0:
                return 0, 0, 0, 0
            else:
                return left, top, width, height

        def get_rect_all(absolute=True):

            size = self.size
            if size is not None and len(size) > 0:
                rect = size[0]
                left = float(rect.get("left"))
                top = float(rect.get("top"))
                right = float(rect.get("right"))
                bottom = float(rect.get("bottom"))
                return left, top, right - left, bottom - top

            left = 1e10
            top = 1e10
            right = -1e10
            bottom = -1e10

            for key, shape in self.shapes.iteritems():
                s_left, s_top, s_width, s_height = get_rect("obj" + key,
                                                            absolute)

                s_right = s_left + s_width
                s_bottom = s_top + s_height

                if s_left < left:
                    left = s_left

                if s_right > right:
                    right = s_right

                if s_top < top:
                    top = s_top

                if s_bottom > bottom:
                    bottom = s_bottom

            return left, top, right - left, bottom - top

        def build_element(tree, element, ctf):
            part = etree.Element("g")

            part.set("id", tree.key)

            transformVal = "matrix(%.2f %.2f %.2f %.2f %.4f %.4f)" % tree.get_matrix()

            if tree.clipDepth is not None:
                part.set("style", "display:none")
            else:
                part.set("transform", transformVal)

            element.append(part)

            if len(tree.ctf) > 0:
                ctf.append({tree.key: tree.ctf})

            if len(tree.children) > 0:
                for c in tree.children:
                    build_element(c, part, ctf)
            else:
                shape = self._search_shape(tree.key)
                if shape is not None:
                    shape_group = Parser.ShapeMaker.make_shape_element(shape, ctf, tree.parent.key)
                    part.append(shape_group)

        abs_left, abs_top, abs_width, abs_height = get_rect_all()
        left, top, width,  height = get_rect_all(False)

        svg = etree.Element("svg", nsmap=Parser.NAMESPACES)
        svg.set("version", "1.1")

        svg.set("viewBox",
                "%.4f %.4f %.4f %.4f" % tuple(PUtil.get_pixel_vals(abs_left, abs_top, abs_width, abs_height)))
        defs = etree.Element("defs")

        dummy_shape = Shape()
        dummy_shape.symbol = ""
        for key, shape in self.shapes.iteritems():
            for defelem in shape.defs:
                defs.append(defelem)
            dummy_shape.edges.extend(shape.edges)

        svg.append(defs)

        build_element(self.tree, svg, [])

        name = dummy_shape.generate_name()

        return name, etree.tostring(svg, pretty_print=True)
        logging.debug("Converted to %s" % filepath)
        logging.debug("Shape : %d %d %d %d" % (left, top, width, height))

    @classmethod
    def save_shape_as_svg(cls, shape, ctf, filepath):
        fp = open(filepath, "w")
        fp.write(etree.tostring(cls.str_shape_as_svg(shape, ctf), pretty_print=True))
        fp.close()

    @classmethod
    def str_shape_as_svg(cls, shape, ctf=[], parent_key=''):
        svg = etree.Element("svg", nsmap=Parser.NAMESPACES)
        svg.set("version", "1.1")
        svg.set("viewBox",
                "%4f %4f %4f %4f" % tuple(PUtil.get_pixel_vals(shape.left, shape.top, shape.width, shape.height)))
        defs = etree.Element("defs")
        for defelem in shape.defs:
            defs.append(defelem)
        svg.append(defs)

        group = cls.ShapeMaker.make_shape_element(shape, ctf, parent_key)

        svg.append(group)
        return svg

    def _build_tree(self, scale_factor=1.0):

        # build tree structure
        root = Tree()
        root.key = "root"
        root.sx = 1.0 / scale_factor
        root.sy = 1.0 / scale_factor
        stack = []

        for k, v in self.places.iteritems():
            tree = Tree()
            tree.set_items(v.items())
            tree.key = "obj" + k
            tree.parent = root
            root.children.append(tree)
            stack.append(tree)

        while len(stack) > 0:
            current = stack.pop()
            currentSprite = self._search_sprite(current.key)
            if currentSprite is not None:
                f = currentSprite.frames[0]
                for p in f.places:
                    for s in p['symbols']:
                        tree = Tree()
                        tree.set_items(p.items())
                        tree.key = LUtil.objectID_from_key(s)
                        tree.parent = current
                        current.children.append(tree)
                        stack.append(tree)

        self.tree = root

    def add_tree(self, tree, element):
        part = etree.Element("part")

        part.set("key", tree.key)

        self._set_vals(part,
                      sx=tree.sx,
                      sy=tree.sy,
                      wx=tree.wx,
                      wy=tree.wy,
                      tx=tree.tx,
                      ty=tree.ty,
                      ctf=tree.ctf,
                      depth=tree.depth,
                      name=tree.name,
                      clipDepth=tree.clipDepth,
                      visible=tree.visible
                      )

        element.append(part)

        for c in tree.children:
            self.add_tree(c, part)

    def _set_vals(self, e, **keyvalue):
        [e.set(k, str(v)) for k,v in keyvalue.iteritems() if v is not None]

    def str_animation(self):
        # build animation
        animations = {}

        for k, v in self.sprites.iteritems():

            if len(v.frames) > 1:

                all_symbols = []

                for f in v.frames:
                    for p in f.places:
                        for s in p['symbols']:
                            if s not in all_symbols:
                                all_symbols.append(s)

                animations.update(self._str_animation(all_symbols, v))


        # save animation file
        animation_set_element = etree.Element("animation_set")

        animation_sequence_element = etree.Element("animation_sequence")
        animation_set_element.append(animation_sequence_element)

        animation_sequence_element.set("index", "1")

        for key, animation in animations.iteritems():

            animation_element = etree.Element("animation")
            animation_element.set("key", key)

            for f in animation.frames:
                frame_element = etree.Element("frame")

                self._set_vals(frame_element,
                              index=f['index'],
                              sx=f['sx'],
                              sy=f['sy'],
                              wx=f['wx'],
                              wy=f['wy'],
                              tx=f['tx'],
                              ty=f['ty'],
                              ctf=f['ctf'],
                              visible=f['visible']
                              )

                animation_element.append(frame_element)

            animation_sequence_element.append(animation_element)
        return animation_set_element

    def _str_animation(self, all_symbols, v):
        animations = {}
        for key in all_symbols:
            animation = Animation()
            psx = 1.0
            psy = 1.0
            pwx = 0.0
            pwy = 0.0
            ptx = 0.0
            pty = 0.0
            pctf = []

            for index, f in enumerate(v.frames):
                sx = None
                sy = None
                wx = None
                wy = None
                tx = None
                ty = None
                ctf = []
                visible = True

                for p in f.places:
                    if key in p['symbols']:
                        sx = p['sx']
                        sy = p['sy']
                        wx = p['wx']
                        wy = p['wy']
                        tx = p['tx']
                        ty = p['ty']
                        ctf = p['ctf']
                        visible = p['visible']
                        break

                if sx is None and sy is None and wx is None and wy is None and tx is None and ty is None:
                    sx = psx
                    sy = psy
                    wx = pwx
                    wy = pwy
                    tx = ptx
                    ty = pty
                    ctf = pctf
                else:
                    if sx is None and sy is None and wx is None and wy is None and tx is not None and ty is not None:
                        if len(animation.frames) > 0:
                            for f in animation.frames:
                                if f['tx'] == tx and f['ty'] == ty:
                                    sx = f['sx']
                                    sy = f['sy']
                                    wx = f['wx']
                                    wy = f['wy']
                                    break

                    if sx is None and sy is None:
                        sx = 1.0
                        sy = 1.0

                    if wx is None and wy is None:
                        wx = 0.0
                        wy = 0.0

                psx = sx
                psy = sy
                pwx = wx
                pwy = wy
                ptx = tx
                pty = ty
                pctf = ctf

                animation.appendFrame(index, sx, sy, wx, wy, tx, ty, ctf, visible)
                animations[key] = animation
        return animations
    

    class ShapeMaker(object):

        @classmethod
        def make_shape_element(cls, shape, ctf, parent_key):

            group = etree.Element("g")
            group.set("id", shape.symbol + "shape")

            for e in shape.edges:

                # line colors
                linecolors = e.get_colors_from_category('l')
                for i, lineColor in zip(xrange(len(linecolors)), linecolors):
                    allpath = []

                    pathElm = Path('line')
                    path = cls._reverse(e.get_path(i, 'line'))
                    if len(path) > 0:
                        if len(e.colors) > 0: 
                            allpath.extend(path)
                            pathElm.set("stroke-width", str(e.lineWidths[i]))
                            pathElm.set("stroke", LUtil.rgb_to_hex(lineColor['l']))
                    merged_allpath_list = cls._merge_path(allpath)

                    all_data = ""

                    for merged_allpath in merged_allpath_list:
                        data = cls._path_data(merged_allpath)
                        all_data += data

                    if len(all_data) > 0:
                        pathElm.set("d", all_data)
                        group.append(pathElm)

                # solid colors
                solidcolors = e.get_colors_from_category('s')
                for i, color in zip(xrange(len(solidcolors)), solidcolors):

                    allpath = []

                    path = e.get_path(i, 'left')
                    if len(path) > 0:
                        allpath.extend(path)

                    path = cls._reverse(e.get_path(i, 'right'))
                    if len(path) > 0:
                        allpath.extend(path)

                    merged_allpath_list = cls._merge_path(allpath)

                    pathElm = Path()
                    clr = color['s']
                    for colorTransform in ctf:
                        if isinstance(clr, tuple):
                            clr = PUtil.colortrans(shape.symbol, color['s'], colorTransform)
                            clr = PUtil.colortrans(parent_key, clr, colorTransform)
                        else: # gradient
                            opacity = PUtil.colortrans_only_alpha(parent_key, colorTransform)/256
                            if opacity > 0.0:
                                pathElm.set("fill-opacity", str(opacity))

                    if isinstance(clr, tuple):
                        pathElm.set("fill", LUtil.rgb_to_hex(clr))
                        if clr[3] < 256:
                            opacity = float(clr[3])/256
                            if opacity > 0.0:
                                pathElm.set("fill-opacity", str(opacity))
                    else:
                        pathElm.set("fill", clr)

                    all_data = ""

                    for merged_allpath in merged_allpath_list:
                        data = cls._path_data(merged_allpath)
                        all_data += data

                    if len(all_data) > 0:
                        pathElm.set("d", all_data)
                        group.append(pathElm)

            if len(ctf) > 0:
                ctf.pop(0)

            return group

        @classmethod
        def _reverse(cls, path):

            if path is None:
                return []

            cx = 0
            cy = 0

            devided_list = []
            devided = None

            for p in path:
                if p['type'] == 'S':
                    if devided is not None:
                        devided_list.append(devided)

                    devided = []

                devided.append(p)

            if devided is not None:
                devided_list.append(devided)

            result = []

            for devided in devided_list:
                for p in devided:

                    if p['type'] == 'S':
                        cx = p['x']
                        cy = p['y']
                    elif p['type'] == 'L':
                        cx += p['x']
                        cy += p['y']
                    elif p['type'] == 'C':
                        cx += p['x1'] + p['x2']
                        cy += p['y1'] + p['y2']

                result.append({'type': 'S', 'x': cx, 'y': cy})

                for p in devided[::-1]:
                    if p['type'] == 'L':
                        result.append({'type': 'L',
                                       'x': -p['x'], 'y': -p['y']})
                        cx -= p['x']
                        cy -= p['y']
                    elif p['type'] == 'C':
                        result.append({'type': 'C',
                                       'x1': -p['x2'],
                                       'y1': -p['y2'],
                                       'x2': -p['x1'],
                                       'y2': -p['y1']})

                        cx -= p['x1'] + p['x2']
                        cy -= p['y1'] + p['y2']

            return result

        @classmethod
        def _path_data(cls, edges):
            data = ""

            for edge in edges:

                if edge['type'] == 'S':
                    data += "M%.4f %.4f " % (edge['x'], edge['y'])

                if edge['type'] == 'L':
                    data += "l%.4f %.4f " % (edge['x'], edge['y'])

                if edge['type'] == 'C':
                    data += "q%.4f %.4f %.4f %.4f " % (edge['x1'], edge['y1'],
                                              edge['x1'] + edge['x2'],
                                              edge['y1'] + edge['y2'])

            return data

        @classmethod
        def _merge_path(cls, path):

            def search_merge_path(sa, anchors, paths):
                for ta, path in zip(anchors, paths):
                    if(round(sa['end'][0],3) == round(ta['begin'][0],3) and
                       round(sa['end'][1],3) == round(ta['begin'][1],3)):
                        return ta, path
                return None, None


            devided_list = []
            devided = None

            for p in path:
                if p['type'] == 'S':
                    if devided is not None:
                        devided_list.append(devided)

                    devided = []

                devided.append(p)

            if devided is not None:
                devided_list.append(devided)

            anchors = []

            for devided in devided_list:
                begin = (devided[0]['x'], devided[0]['y'])

                ex = 0.0
                ey = 0.0

                for p in devided:
                    if p['type'] == 'S':
                        ex = p['x']
                        ey = p['y']
                    elif p['type'] == 'L':
                        ex += p['x']
                        ey += p['y']
                    elif p['type'] == 'C':
                        ex += p['x1'] + p['x2']
                        ey += p['y1'] + p['y2']

                end = (ex, ey)

                anchors.append({'begin': begin, 'end': end})

            if len(devided_list) <= 0:
                return []

            results = []
            result = [devided_list.pop()]
            results.append(result)

            result_anchors = [anchors.pop()]

            while len(devided_list) > 0:
                next_anchor, next_path = search_merge_path(result_anchors[-1],
                                                           anchors, devided_list)

                if next_path is not None:
                    result.append(next_path)
                    result_anchors.append(next_anchor)

                    devided_list.remove(next_path)
                    anchors.remove(next_anchor)
                else:
                    result = []
                    results.append(result)

                    result.append(devided_list[0])
                    result_anchors.append(anchors[0])

                    devided_list.remove(devided_list[0])
                    anchors.remove(anchors[0])

            merged_list = []

            for result in results:
                merged = []
                merged.append(result[0][0])
                merged_list.append(merged)

                for r in result:
                    for p in r:
                        if p['type'] != 'S':
                            merged.append(p)

            return merged_list



class PUtil(object):

    @staticmethod
    def get_pixel_vals(*twips): 
        if len(twips) == 1:
            return float(twips[0])/20
        return [float(t)/20 if t is not None else None for t in twips]

    @staticmethod
    def convert_color_as_tuple(elm):
        alpha = elm.get('alpha')
        if alpha is None :
            alpha = 256
        return int(elm.get('red')), int(elm.get('green')), int(elm.get('blue')), int(alpha)


    @staticmethod
    def colortrans(key, rgba, ctf):
        if len(ctf) == 0:
            return rgba

        c = Color(rgba[:4])
        if ctf.has_key(key):
            colorTransform = ColorTransform(ctf[key])
            return c.transform(colorTransform).get_colors()
        else:
            return c.get_colors()

    @staticmethod
    def colortrans_only_alpha(key, ctf):

        def trans_color(rgba, factor, offset):
            return max(0, min( ( float(rgba * int(factor)) / 256 + int(offset) ), 255 ))

        if ctf.has_key(key):
            return trans_color(256, ctf[key][3], ctf[key][7])

        return 0.0


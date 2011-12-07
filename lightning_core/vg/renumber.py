# resolving lightning depth-object problem
from __future__ import with_statement
from lxml import etree
import sys
from copy import deepcopy


class PlaceObject(object):
    def __init__(self, depth, objectID=None, transform=None, color_transform=None, enable=True):
        self.depth = depth
        self.objectID = objectID
        self.transform = transform
        self.color_transform = color_transform
        self.enable = enable

    def transform_element(self):
        if self.transform is None:
            return None
        elem = etree.Element('transform')
        trans = etree.Element('Transform')
        for k, v in self.transform.iteritems():
            trans.set(k, v)
        elem.append(trans)
        return elem

    def color_transform_element(self):
        if self.color_transform is None:
            return None
        elem = etree.Element('colorTransform')
        trans = etree.Element('ColorTransform2')
        for k, v in self.color_transform.iteritems():
            trans.set(k, v)
        elem.append(trans)
        return elem


class PlaceObjectFactory(object):
    def _generate_transform(self, place_object):
        for trans in place_object.xpath('transform/Transform'):
            return deepcopy(dict(trans.attrib))
        return None

    def _generate_color_transform(self, place_object):
        for trans in place_object.xpath('colorTransform/ColorTransform2'):
            return deepcopy(dict(trans.attrib))
        return None
        
    def generate(self, place_object, ext_objectID=None):
        if place_object.tag != 'PlaceObject2':
            return None
        depth = int(place_object.get('depth'))
        objectID = place_object.get('objectID')
        if objectID is not None:
            objectID = int(objectID)
        elif ext_objectID is not None:
            objectID = ext_objectID
        transform = self._generate_transform(place_object)
        color_transform = self._generate_color_transform(place_object)
        return PlaceObject(depth, objectID, transform, color_transform)


class Renumber(object):
    def __init__(self):
        self.parsed = None
        self.sprite_depth_obj = {}
        self.factory = PlaceObjectFactory()

    def load_xmlstring(self, xml):
        self.parsed = etree.XML(xml)

    def load_xmlfile(self, filename):
        with open(filename) as f:
            self.parsed = etree.parse(f)

    def create_table_depth_object(self):
        if self.parsed is None:
            print('Run renumber.load_xmlfile first')
            return
        self.sprite_depth_obj = {}
        for sprite in self.parsed.xpath('/swf/Header/tags/DefineSprite'):
            sprite_id = sprite.get('objectID')
            if sprite_id is None:
                break
            frames = int(sprite.get('frames', 1))
            # print('sprite_id=%d, frames=%d' % (sprite_id, frames))
            if frames > 1:
                depth_obj = {}
                for po in sprite.xpath('tags/PlaceObject2'):
                    depth = int(po.get('depth'))
                    po_id = po.get('objectID')
                    if depth not in depth_obj:
                        depth_obj[depth] = set()
                    if po_id is not None:
                        depth_obj[depth].add(int(po_id))
                self.sprite_depth_obj[int(sprite_id)] = depth_obj
        return self.sprite_depth_obj

    def get_renumber_sprite_ids(self):
        result = []
        for sprite_id, depth_obj in self.sprite_depth_obj.iteritems():
            for depth, objects in depth_obj.iteritems():
                # print sprite_id, depth, objects
                if len(objects) > 1:
                    result.append(sprite_id)
        return list(set(result))

    def create_renumbered_table(self, depth_obj):
        result = {}
        renumbered_depth = 1
        for depth in sorted(depth_obj.keys()):
            objects = sorted(list(depth_obj[depth]))
            for obj in objects:
                result[renumbered_depth] = (depth, obj) # (parent_depth, objectID)
                renumbered_depth += 1
        return result

    def create_frames_depth_object(self, sprite_id):
        result = []
        depth_obj = {}
        for elem in self.parsed.xpath('/swf/Header/tags/DefineSprite[@objectID="%d"]/tags/*' % sprite_id):
            if elem.tag == 'ShowFrame':
                if len(result) > 0:
                    for depth in result[-1].keys():
                        if depth not in depth_obj:
                            place_object = result[-1][depth]
                            depth_obj[depth] = deepcopy(place_object)
                deletable_depth_list = []
                for depth, obj in depth_obj.iteritems():
                    if obj is None and depth in depth_obj:
                        deletable_depth_list.append(depth)
                for d in deletable_depth_list:
                    del depth_obj[d]
                result.append(depth_obj)
                depth_obj = {}
            elif elem.tag == 'RemoveObject2':
                depth = int(elem.get('depth'))
                depth_obj[depth] = None
            elif elem.tag == 'PlaceObject2':
                depth = int(elem.get('depth'))
                objectID = elem.get('objectID')
                if objectID is not None:
                    temp_place_object = self.factory.generate(elem)
                    if temp_place_object.transform is not None or temp_place_object.color_transform is not None:
                        depth_obj[depth] = temp_place_object
                    elif len(result) > 0 and depth in result[-1]:
                        temp_place_object = deepcopy(result[-1][depth])
                        temp_place_object.objectID = int(objectID)
                        depth_obj[depth] = temp_place_object
                else:
                    if len(result) > 0 and depth in result[-1]:
                        objectID = result[-1][depth].objectID
                        depth_obj[depth] = self.factory.generate(elem, objectID)
        return result

    def renumber_object(self, renumbered_table, frames_depth_object, sprite_id):
        frame_index = 0
        for elem in self.parsed.xpath('/swf/Header/tags/DefineSprite[@objectID="%d"]/tags/*' % sprite_id):
            if elem.tag == 'ShowFrame':
                frame_index += 1
            elif elem.tag == 'RemoveObject2':
                depth = int(elem.get('depth'))
                frame_depth_obj = frames_depth_object[frame_index-1]
                for renum_depth, value in renumbered_table.iteritems():
                    old_depth = value[0]
                    objectID = value[1]
                    if old_depth == depth and depth in frame_depth_obj and frame_depth_obj[depth].objectID == objectID:
                        elem.set('depth', str(renum_depth))
            elif elem.tag == 'PlaceObject2':
                depth = int(elem.get('depth'))
                frame_depth_obj = frames_depth_object[frame_index]
                for renum_depth, value in renumbered_table.iteritems():
                    old_depth = value[0]
                    objectID = value[1]
                    if old_depth == depth and depth in frame_depth_obj and frame_depth_obj[depth].objectID == objectID:
                        # print frame_index, depth, renum_depth, objectID
                        po = frame_depth_obj[depth]
                        elem.set('depth', str(renum_depth))
                        if len([e for e in elem.xpath('transform')]) == 0:
                            t = po.transform_element()
                            if t is not None:
                                elem.append(t)
                        if len([e for e in elem.xpath('colorTransform')]) == 0:
                            c = po.color_transform_element()
                            if c is not None:
                                elem.append(c)
                        if len(self.sprite_depth_obj[sprite_id][depth]) > 1:
                            obj_remove = frames_depth_object[frame_index-1].values()
                            depth_remove = None
                            can_remove = False
                            for k, v in renumbered_table.iteritems():
                                if v[0] == old_depth and v[1] in [ob.objectID for ob in obj_remove]:
                                    depth_remove = k
                                    can_remove = (objectID != v[1])
                            if depth_remove is not None and can_remove:
                                if int(elem.get('replace')) == 1:
                                    elem.set('replace', '0')
                                # print('add RemoveObject2 depth="%d" into frame: %d' % (depth_remove, frame_index))
                                ro = etree.Element('RemoveObject2')
                                ro.set('depth', str(depth_remove))
                                elem.addprevious(ro)

    def renumber(self):
        self.create_table_depth_object()
        sprite_ids = self.get_renumber_sprite_ids()
        if len(sprite_ids) == 0:
            return self.parsed
        for sprite_id in sprite_ids:
            depth_object = self.sprite_depth_obj[sprite_id]
            renumbered_table = self.create_renumbered_table(depth_object)
            frames_depth_object = self.create_frames_depth_object(sprite_id)
            self.renumber_object(renumbered_table, frames_depth_object, sprite_id)
        return self.parsed

    def write(self, filename):
        self.parsed.write(filename, pretty_print=True)

    def __str__(self):
        return etree.tostring(self.parsed, pretty_print=True)

if __name__ == '__main__':
    filename = sys.argv[1]
    renumber = Renumber()
    renumber.load_xmlfile(filename)
    renumber.renumber()
    renumber.write(filename)

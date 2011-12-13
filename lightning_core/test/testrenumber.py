import unittest
from lightning_core.vg.renumber import *
from lxml import etree

class TestPlaceObject(unittest.TestCase):
    
    SAMPLE_OBJECT = '''
          <PlaceObject2 replace="0" depth="6" objectID="7">
            <transform>
              <Transform scaleX="0.5" scaleY="0.5" skewX="0.3" skewY="-0.3" transX="334" transY="624"/>
            </transform>
            <colorTransform>
              <ColorTransform2 factorRed="-46" factorGreen="210" factorBlue="256" factorAlpha="256" offsetRed="-128" offsetGreen="71" offsetBlue="224" offsetAlpha="0"/>
            </colorTransform>
          </PlaceObject2>
        '''

    def setUp(self):
        self.factory = PlaceObjectFactory()
        self.sample = etree.XML(self.SAMPLE_OBJECT)

    def test_generate(self):
        po = self.factory.generate(self.sample)
        self.assertEqual(po.depth, 6)
        self.assertEqual(po.objectID, 7)
        self.assertEqual(po.transform['scaleX'], '0.5')
        self.assertEqual(po.transform['scaleY'], '0.5')
        self.assertEqual(po.transform['skewX'], '0.3')
        self.assertEqual(po.transform['skewY'], '-0.3')
        self.assertEqual(po.transform['transX'], '334')
        self.assertEqual(po.transform['transY'], '624')
        self.assertEqual(po.color_transform['factorRed'], '-46')
        self.assertEqual(po.color_transform['factorGreen'], '210')
        self.assertEqual(po.color_transform['factorBlue'], '256')
        self.assertEqual(po.color_transform['factorAlpha'], '256')
        self.assertEqual(po.color_transform['offsetRed'], '-128')
        self.assertEqual(po.color_transform['offsetGreen'], '71')
        self.assertEqual(po.color_transform['offsetBlue'], '224')
        self.assertEqual(po.color_transform['offsetAlpha'], '0')


class TestRenumber(unittest.TestCase):
    SAMPLE_SPRITE = '''
<swf version="4" compressed="0">
  <Header framerate="12" frames="1">
    <tags>
      <DefineSprite objectID="7" frames="3">
        <tags>
          <PlaceObject2 replace="0" depth="1" objectID="4">
            <transform>
              <Transform transX="0" transY="0"/>
            </transform>
          </PlaceObject2>
          <ShowFrame/>
          <PlaceObject2 replace="1" depth="1" objectID="5"/>
          <ShowFrame/>
          <PlaceObject2 replace="1" depth="1" objectID="6"/>
          <ShowFrame/>
          <End/>
        </tags>
      </DefineSprite>
    </tags>
  </Header>
</swf>
    '''

    def setUp(self):
        self.renumber = Renumber()
        self.renumber.load_xmlstring(self.SAMPLE_SPRITE)


    def test_create_table_depth_object(self):
        sprite_depth_object = self.renumber.create_table_depth_object()
        self.assertEqual(len(sprite_depth_object), 1)
        self.assert_(7 in sprite_depth_object)
        self.assert_(1 in sprite_depth_object[7])
        objects = list(sprite_depth_object[7][1])
        self.assertEqual(len(objects), 3)
        self.assertEqual(objects[0], 4)
        self.assertEqual(objects[1], 5)
        self.assertEqual(objects[2], 6)

    def test_get_renumber_sprite_ids(self):
        self.renumber.create_table_depth_object()
        sprite_ids = self.renumber.get_renumber_sprite_ids()
        self.assertEqual(len(sprite_ids), 1)
        self.assertEqual(sprite_ids[0], 7)

    def test_create_renumbered_table(self):
        sprite_depth_object = self.renumber.create_table_depth_object()
        self.assert_(7 in sprite_depth_object)
        depth_object = sprite_depth_object[7]
        renumbered_table = self.renumber.create_renumbered_table(depth_object)
        self.assertEqual(len(renumbered_table), 3)
        self.assert_(1 in renumbered_table)
        self.assertEqual(renumbered_table[1], (1,4))
        self.assert_(2 in renumbered_table)
        self.assertEqual(renumbered_table[2], (1,5))
        self.assert_(3 in renumbered_table)
        self.assertEqual(renumbered_table[3], (1,6))

    def test_create_frames_depth_object(self):
        self.renumber.create_table_depth_object()
        frames_depth_object = self.renumber.create_frames_depth_object(7)
        self.assertEqual(len(frames_depth_object), 3)
        self.assert_(1 in frames_depth_object[0])

        obj0 = frames_depth_object[0][1]
        self.assertEqual(obj0.objectID, 4)
        self.assertEqual(obj0.depth, 1)
        self.assertEqual(obj0.transform['transX'], '0')
        self.assertEqual(obj0.transform['transY'], '0')

        obj1 = frames_depth_object[1][1]
        self.assert_(1 in frames_depth_object[1])
        self.assertEqual(obj1.objectID, 5)
        self.assertEqual(obj1.depth, 1)
        self.assertEqual(obj1.transform['transX'], '0')
        self.assertEqual(obj1.transform['transY'], '0')

        self.assert_(1 in frames_depth_object[2])
        obj2 = frames_depth_object[2][1]
        self.assertEqual(obj2.objectID, 6)
        self.assertEqual(obj2.depth, 1)
        self.assertEqual(obj2.transform['transX'], '0')
        self.assertEqual(obj2.transform['transY'], '0')

    def test_renumber(self):
        self.renumber.renumber()
        depth_object = {}
        for elem in self.renumber.parsed.xpath('//DefineSprite/tags/PlaceObject2'):
            depth = elem.get('depth')
            obj = elem.get('objectID')
            if obj is not None:
                self.failIf(depth in depth_object and obj != depth_object[depth])
                depth_object[depth] = obj


if __name__ == '__main__':
    unittest.main()

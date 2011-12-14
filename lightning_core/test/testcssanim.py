import unittest
from lightning_core.vg.cssanim import *
from lxml import etree

class TestSvgShape(unittest.TestCase):
    def test_constructor(self):
        elm = ('obj','hash',1,2,3,4)
        svgShape = SvgShape(elm)
        self.assertEqual(svgShape.obj   ,elm[0])
        self.assertEqual(svgShape.hash  ,elm[1])
        self.assertEqual(svgShape.left  ,elm[2])
        self.assertEqual(svgShape.top   ,elm[3])
        self.assertEqual(svgShape.width ,elm[4])
        self.assertEqual(svgShape.height,elm[5])
        self.assertEqual(svgShape.symbol,'')
        self.assertEqual(svgShape.edges ,[])

class TestSvgTransform(unittest.TestCase):
    def make_sample_constructor(self):
        hoge = etree.Element('hoge')
        hoge.set('sx','100')
        hoge.set('sy','200')
        hoge.set('wy','220')
        hoge.set('tx','101')
        hoge.set('ty','202')
        hoge.set('depth','8')
        hoge.set('ctf','[10,20,-30,40,50,60,70,80]')
        hoge.set('clipDepth','88')
        hoge.set('visible','False')
        return SvgTransform(hoge.attrib)

    def test_eq(self):
        st1 = self.make_sample_constructor()
        st2 = self.make_sample_constructor()
        self.assertTrue(st1 == st2)

        st1.sx=1.0
        self.assertFalse(st1 == st2)

        st2.sx=1.0
        self.assertTrue(st1 == st2)

        st1.name='st1'
        st1.clipDepth = 100
        self.assertTrue(st1 == st2)

    def test_constructor(self):
        hoge = etree.Element('hoge')
        st = SvgTransform(hoge.attrib)
        self.assertEqual(st.sx,1.0)
        self.assertEqual(st.sy,1.0)
        self.assertEqual(st.wx,0.0)
        self.assertEqual(st.wy,0.0)
        self.assertEqual(st.tx,0.0)
        self.assertEqual(st.ty,0.0)
        self.assertEqual(st.depth,1)
        self.assertEqual(st.ctf,[])
        self.assertEqual(st.clipDepth,None)
        self.assertEqual(st.visible,True)

        st2 = self.make_sample_constructor()
        self.assertEqual(st2.sx,100)
        self.assertEqual(st2.sy,200)
        self.assertEqual(st2.wx,0.0)
        self.assertEqual(st2.wy,220)
        self.assertEqual(st2.tx,101)
        self.assertEqual(st2.ty,202)
        self.assertEqual(st2.depth,8)
        self.assertEqual(st2.ctf,[10,20,-30,40,50,60,70,80])
        self.assertEqual(st2.clipDepth,88)
        self.assertEqual(st2.visible,False)

    def test_write_matrix(self):
        st = self.make_sample_constructor()
        result = st.write_matrix()
        self.assertEqual(result,'matrix(100.0,0.0,220.0,200.0,5.050000,10.100000)')

    def test_write_webkit_transform(self):
        st = self.make_sample_constructor()
        result = st.write_webkit_transform()
        self.assertEqual(result,'-webkit-transform: matrix3d(100.0,0.0,0,0,220.0,200.0,0,0,0,0,1,0,5.050000,10.100000,0,1);')

    def test_write_visible(self):
        st = self.make_sample_constructor()
        self.assertEqual(st.write_visible(),'opacity: 0.0;')
        st.visible=True
        self.assertEqual(st.write_visible(),'opacity: 0.468750;')

class TestAnimationManager(unittest.TestCase):
    def setUp(self):
        self.dir_path = ''
        self.basefilename = ''
        lines = ['obj15 hash 0 0 200 300']
        self.manager = AnimationManager(self.dir_path, self.basefilename)
        self.shape_table = self.manager.get_shapes(lines)
        self.anim_table = self.manager.get_animation(self.animation_tree())
        svg = etree.Element('svg')
        svg.set('name', 'dummy svg shape')
        parser_shapes = {'15':self.shape_table['obj15']}
        self.structure_table, self.structure_tree = self.manager.get_structure(self.structure_root(), self.shape_table, self.anim_table, [], parser_shapes)

    def test_constructor(self):
        manager = AnimationManager(self.dir_path, self.basefilename)
        self.assertEqual(manager.dir_path, '')
        self.assertEqual(manager.shapes_filepath, 'shapes')
        self.assertEqual(manager.animation_filepath, 'animation.xml')
        self.assertEqual(manager.structure_filepath, 'structure.xml')
        self.assertEqual(manager.cssfilepath, './.css')
        self.assertEqual(manager.htmlfilepath, './.html')
        self.assertEqual(manager.xmlfilename, '')

    def test_get_shapes(self):
        self.assert_('obj15' in self.shape_table)
        shape = self.shape_table['obj15']
        self.assertEqual(shape.obj, 'obj15')
        self.assertEqual(shape.hash, 'hash')
        self.assertEqual(shape.left, 0)
        self.assertEqual(shape.top, 0)
        self.assertEqual(shape.width, 200)
        self.assertEqual(shape.height, 300)

    def animation_tree(self):
        def make_frame(index, sx,sy, wx,wy, tx,ty, visible, ctf):
            frame = etree.Element('frame')
            frame.set('index', str(index))
            frame.set('sx', str(sx))
            frame.set('sy', str(sy))
            frame.set('wx', str(wx))
            frame.set('wy', str(wy))
            frame.set('tx', str(tx))
            frame.set('ty', str(ty))
            frame.set('visible', str(visible))
            frame.set('ctf', str(ctf))
            return frame

        root = etree.Element('animation_set')
        anim_seq = etree.Element('animation_sequence')
        anim_seq.set('index', '1')
        anim = etree.Element('animation')
        anim.set('key', '-obj16-33')
        frame0  = make_frame(0 , 1.0,1.0, 356.0,-44.0, 0.0,0.0, False, [])
        frame1  = make_frame(1 , 1.0,1.0, 356.0,-44.0, 0.0,0.0, False, [])
        frame14 = make_frame(14, 1.10000610352,1.19999694824, 329.0,-77.0, 0.0,0.0, True, [0,1,10,256,100,300,256,0])
        frame16 = make_frame(16, 1.0,1.0, 356.0,-44.0, 0.0,0.0, False, [])
        anim.append(frame0)
        anim.append(frame1)
        anim.append(frame14)
        anim.append(frame16)
        anim_seq.append(anim)
        root.append(anim_seq)
        return root

    def structure_root(self):
        def make_part(key, sx,sy, wx,wy, tx,ty, ctf, depth, name=None, clipDepth=None, visible=True):
            part = etree.Element('part')
            part.set('key', key)
            part.set('sx', str(sx))
            part.set('sy', str(sy))
            part.set('wx', str(wx))
            part.set('wy', str(wy))
            part.set('tx', str(tx))
            part.set('ty', str(ty))
            part.set('ctf', str(ctf))
            part.set('depth', str(depth))
            if name is not None:
                part.set('name', name)
            if clipDepth is not None:
                part.set('clipDepth', str(clipDepth))
            part.set('visible', str(visible))
            return part

        root = etree.Element('structure')
        sprite = make_part('obj16', 1.0,1.0, 356.0,-44.0, 0.0,0.0, [], 33, name='hoge', visible=False)
        root.append(sprite)
        
        shape = make_part('obj15', 2.0,2.0, 0.5,0.0, -1.0,-2.0, [], 1, clipDepth="4", visible=True)
        sprite.append(shape)

        return root

    def test_get_animation(self):
        def assert_frame(frame, index, sx,sy, wx,wy, tx,ty, ctf, visible):
            self.assertAlmostEqual(frame.sx, sx)
            self.assertAlmostEqual(frame.sy, sy)
            self.assertAlmostEqual(frame.wx, wx)
            self.assertAlmostEqual(frame.wy, wy)
            self.assertAlmostEqual(frame.tx, tx)
            self.assertAlmostEqual(frame.ty, ty)
            self.assertEqual(frame.ctf, ctf)
            self.assertAlmostEqual(frame.visible, visible)

        self.assertEqual(len(self.anim_table), 1)
        self.assert_('-obj16-33' in self.anim_table)
        animation = self.anim_table['-obj16-33']
        self.assertEqual(len(animation), 4)
        frame0  = animation[0]
        frame1  = animation[1]
        frame14 = animation[2]
        frame16 = animation[3]
        assert_frame(frame0 ,  0,  1.0,1.0, 356.0,-44.0, 0.0,0.0, [], False)
        assert_frame(frame1 ,  1,  1.0,1.0, 356.0,-44.0, 0.0,0.0, [], False)
        assert_frame(frame14, 14,  1.10000610352,1.19999694824, 329.0,-77.0, 0.0,0.0, [0,1,10,256,100,300,256,0], True)
        assert_frame(frame16, 16,  1.0,1.0, 356.0,-44.0, 0.0,0.0, [], False)

    def test_get_structure(self):
        def assert_frame(frame, key, sx,sy, wx,wy, tx,ty, ctf, depth, visible):
            self.assertAlmostEqual(frame.sx, sx)
            self.assertAlmostEqual(frame.sy, sy)
            self.assertAlmostEqual(frame.wx, wx)
            self.assertAlmostEqual(frame.wy, wy)
            self.assertAlmostEqual(frame.tx, tx)
            self.assertAlmostEqual(frame.ty, ty)
            self.assertEqual(frame.ctf, ctf)
            self.assertEqual(frame.depth, depth)
            self.assertAlmostEqual(frame.visible, visible)

        frame = self.structure_table['-obj16-33']
        assert_frame(frame, 'obj16', 1.0,1.0, 356.0,-44.0, 0.0,0.0, [], 33, False)

        frame = self.structure_table['-obj15-1']
        assert_frame(frame, 'obj15', 2.0,2.0, 0.5,0.0, -1.0,-2.0, [], 1, True)

        self.assertEqual(self.structure_tree.tag, 'structure')
        self.assertEqual(len(self.structure_tree), 1)
        div1 = self.structure_tree[0]
        self.assertEqual(div1.tag, 'div')
        self.assertEqual(div1.get('class'), '-obj16-33')
        self.assertEqual(div1.get('id'), 'hoge')
        self.assertEqual(len(div1), 1)
        div2 = div1[0]
        self.assertEqual(div2.tag, 'div')
        self.assertEqual(div2.get('class'), '-obj15-1')
        self.assertEqual(div2.get('style'), 'display:none;')
        self.assertEqual(len(div2), 1)
        div3 = div2[0]
        self.assertEqual(div3.tag, 'div')
        self.assertEqual(div3.get('class'), '-obj15-shape')
        shape = div3[0]
        self.assertEqual(shape.tag, 'svg')
        self.assertEqual(shape.get('version'), '1.1')
        self.assertEqual(shape.get('viewBox'), '0.000000 0.000000 10.000000 15.000000')

    def test__remove_deplicated_keyframes(self):
        elements = [(0.0 , 'hoge'),
                    (10.0, 'hoge'),
                    (20.0, 'hoge'),
                    (30.0, 'hoge'),
                    (40.0, 'hoge'),
                    (50.0, 'hoge'),
                    (60.0, 'hige'),
                    (70.0, 'hoge')]
        result = self.manager._remove_deplicated_keyframes(elements)
        self.assertEqual(result, [(0.0, 'hoge'),(50.0, 'hoge'),(60.0,'hige'),(70.0,'hoge')])

    def test__interpolate_keyframes(self):
        self.animation_tree()
        elm = etree.Element('hoge')
        visibleSvg = SvgTransform(elm.attrib)
        unvisibleSvg = SvgTransform(elm.attrib)
        unvisibleSvg.visible = False
        elements = [(0.0 , visibleSvg),
                    (50.0, unvisibleSvg),
                    (60.0, unvisibleSvg),
                    (70.0, visibleSvg)]
        eps=0.1
        result = self.manager._interpolate_keyframes(elements,eps)
        self.assertEquals(result,[(0.0, visibleSvg),(50.0-eps, visibleSvg),(50.0, unvisibleSvg),(60.0, unvisibleSvg),(70.0-eps, unvisibleSvg),(70.0, visibleSvg),(100.0, visibleSvg)])

    def test_write_div(self):
        div = self.manager.write_div(self.structure_tree)
        self.assertEqual(div,'''<structure>
  <div class="-obj16-33" id="hoge">
    <div class="-obj15-1" style="display:none;">
      <div class="-obj15-shape">
        <svg xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0.000000 0.000000 10.000000 15.000000">
          <defs/>
          <g id="shape"/>
        </svg>
      </div>
    </div>
  </div>
</structure>
''')

    def test_write_css(self):
        css = self.manager.write_css(self.structure_table, self.shape_table, self.anim_table, '', True)
        expected = '''svg { display:block; }
@-webkit-keyframes -obj16-33 {
0.000000% { -webkit-transform: matrix3d(1.0,356.0,0,0,-44.0,1.0,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
25.000000% { -webkit-transform: matrix3d(1.0,356.0,0,0,-44.0,1.0,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
49.999900% { -webkit-transform: matrix3d(1.100006,329.0,0,0,-77.0,1.199997,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
50.000000% { -webkit-transform: matrix3d(1.100006,329.0,0,0,-77.0,1.199997,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 1.0; }
74.999900% { -webkit-transform: matrix3d(1.100006,329.0,0,0,-77.0,1.199997,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 1.0; }
75.000000% { -webkit-transform: matrix3d(1.0,356.0,0,0,-44.0,1.0,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
100.000000% { -webkit-transform: matrix3d(1.0,356.0,0,0,-44.0,1.0,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
}

.-obj15-1 {
position: absolute;
-webkit-transform-origin: 0.0px 0.0px;
-webkit-transform: matrix(2.0,0.500000,0.0,2.0,-0.050000,-0.100000);
}


.-obj16-33 {
-webkit-animation-name: -obj16-33;
-webkit-animation-iteration-count: infinite;
-webkit-animation-timing-function: linear;
-webkit-transform-origin: 0.0px 0.0px;
-webkit-animation-duration: 0.333333s;
-webkit-transform: matrix(1.0,356.0,-44.0,1.0,0.0,0.0);
position: absolute;
}


.-obj15-shape {
top: 0px;
height: 15px;
width: 10px;
-webkit-transform: matrix(1.0,0.0,0.0,1.0,0.0,0.0);
position: absolute;
left: 0px;
}
'''
        self.assertEqual(css, expected)

    def test__make_keyframes(self):
        keyframes = self.manager._make_keyframes(self.anim_table)
        expected = '''@-webkit-keyframes -obj16-33 {
0.000000% { -webkit-transform: matrix3d(1.0,356.0,0,0,-44.0,1.0,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
25.000000% { -webkit-transform: matrix3d(1.0,356.0,0,0,-44.0,1.0,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
49.999900% { -webkit-transform: matrix3d(1.100006,329.0,0,0,-77.0,1.199997,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
50.000000% { -webkit-transform: matrix3d(1.100006,329.0,0,0,-77.0,1.199997,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 1.0; }
74.999900% { -webkit-transform: matrix3d(1.100006,329.0,0,0,-77.0,1.199997,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 1.0; }
75.000000% { -webkit-transform: matrix3d(1.0,356.0,0,0,-44.0,1.0,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
100.000000% { -webkit-transform: matrix3d(1.0,356.0,0,0,-44.0,1.0,0,0,0,0,1,0,0.0,0.0,0,1); opacity: 0.0; }
}'''
        self.assertEqual(keyframes, expected)

    def test__make_transform(self):
        transforms = self.manager._make_transform(self.structure_table, self.shape_table, self.anim_table)
        expected = '''.-obj15-1 {
position: absolute;
-webkit-transform-origin: 0.0px 0.0px;
-webkit-transform: matrix(2.0,0.500000,0.0,2.0,-0.050000,-0.100000);
}


.-obj16-33 {
-webkit-animation-name: -obj16-33;
-webkit-animation-iteration-count: infinite;
-webkit-animation-timing-function: linear;
-webkit-transform-origin: 0.0px 0.0px;
-webkit-animation-duration: 0.333333s;
-webkit-transform: matrix(1.0,356.0,-44.0,1.0,0.0,0.0);
position: absolute;
}


.-obj15-shape {
top: 0px;
height: 15px;
width: 10px;
-webkit-transform: matrix(1.0,0.0,0.0,1.0,0.0,0.0);
position: absolute;
left: 0px;
}
'''
        self.assertEqual(transforms, expected)

if __name__ == '__main__':
    unittest.main()

import unittest
from lightning_core.vg.swf import *
from lightning_core.vg.parser import *
from lxml import etree


class TestPlace(unittest.TestCase):

    def test_constructor(self):
        tNone = []
        ctNone = []

        placeNone = Place(tNone, ctNone, None, None, None, None)
        self.assert_place_const(placeNone, None, None,None,None,None,None,None,None,None,None,[])

        ts = [{'scaleX':'0','scaleY':'1000'}]
        tw = [{'skewX' :'1.0909','skewY':'0.0002'}]
        tt = [{'transX':'1111','transY':'255'}]
        cf = [{'factorRed':256, 'factorGreen':18, 'factorBlue':0}]
        co = [{'offsetRed':0, 'offsetGreen':255, 'offsetBlue':1}]

        place1 = Place(ts, cf,'3', '1', 'hoge', '100')
        self.assert_place_const(place1, '3', 0, 1000 ,None,None,None,None,'1','hoge','100',[256,18, 0, 256, 0,0,0,0])

        place2 = Place(tw, co, '5', '0', 'hoge', '0')
        self.assert_place_const(place2, '5', None,None ,1.0909,0.0002, None,None,'0','hoge','0',[256,256, 256, 256, 0,255,1,0])

        place3 = Place(tt, co, '5', '0', 'hoge', '0')
        self.assert_place_const(place3, '5', None,None , None,None, 1111,255,'0','hoge','0',[256,256, 256, 256, 0,255,1,0])

    def test_set_and_getitem(self):
        place = Place([], [], None, None, None, None)
        place['tx'] = 100.0
        self.assertEqual(place['tx'], 100.0)

    def assert_place_const(self, place, objectId, sx,sy, wx,wy, tx,ty, depth, name, clipDepth, ctf):

        self.assertEqual(place.id, objectId)
        self.assertEqual(place.depth, depth)
        self.assertEqual(place.swf_depth, 1)
        self.assertEqual(place.clipDepth, clipDepth)
        self.assertEqual(place.name, name)
        self.assertEqual(place.visible, True)
        self.assertEqual(place.symbols, [])

        self.assertEqual(place.sx, sx)
        self.assertEqual(place.sy, sy)
        self.assertEqual(place.wx, wx)
        self.assertEqual(place.wy, wy)
        self.assertEqual(place.tx, tx)
        self.assertEqual(place.ty, ty)

        self.assertEqual(place.ctf, ctf)


class TestFrame(unittest.TestCase):
    def test_constructor(self):
        frame = Frame()
        self.assertEqual(len(frame.places), 0)
        self.assertEqual(len(frame), 0)

    def test_addPlace(self):
        frame = Frame()
        matrixDict = {'sx': 2.0, 'sy': 1.0, 'wx':0 , 'wy': 0, 'tx': -1.0, 'ty': -2.1 ,'ctf':[], 'depth':2, 'clipDepth':1}
        symbols = []
        name = 'hoge'
        frame.addPlace(matrixDict, symbols, name)
        self.assertEqual(len(frame), 1)
        place = frame.places[0]
        self.assertAlmostEqual(place['sx'], 2.0)
        self.assertAlmostEqual(place.sx, 2.0)
        self.assertAlmostEqual(place.sy, 1.0)
        self.assertAlmostEqual(place.wx, 0.0)
        self.assertAlmostEqual(place.wy, 0.0)
        self.assertAlmostEqual(place.tx, -1.0)
        self.assertAlmostEqual(place.ty, -2.1)
        self.assertEqual(place.ctf, [])
        self.assertEqual(place.swf_depth, 2)
        self.assertEqual(place.name, 'hoge')
        self.assertEqual(place.symbols, [])

class TestSprite(unittest.TestCase):
    def test_constructor(self):
        sprite = Sprite()
        self.assertEqual(sprite.symbol, '')
        self.assertEqual(len(sprite.frames), 0)
        self.assertEqual(len(sprite), 0)

    def test_addFrame(self):
        sprite = Sprite()
        sprite.addFrame(None)
        sprite.symbol = 'hoge'
        self.assertEqual(sprite.symbol, 'hoge')
        self.assertEqual(len(sprite), 1)

    def test_searchSymbols(self):
        frame = Frame()
        matrixDict = {'sx': 1, 'sy': 1, 'wx':0 , 'wy': 0, 'tx': 0, 'ty': 0 , 'ctf': 0, 'depth':1, 'clipDepth':1}
        symbols = ['test']
        name = 'hoge'
        frame.addPlace(matrixDict, symbols, name)
        sprite = Sprite()
        sprite.addFrame(frame)
        self.assertEqual(len(sprite), 1)
        symbols = sprite.searchSymbols(1)
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0], 'test')

class TestEdge(unittest.TestCase):
    def test_constructor(self):
        edge = Edge()
        self.assertEqual(len(edge.colors), 0)
        self.assertEqual(len(edge.values), 0)

    def test_add(self):
        edge = Edge()
        edge.add({'type':'S', 'fl':0})
        self.assertEqual(len(edge.values), 1)

    def test_get_path(self):
        edge = Edge()
        edge.add({'type':'S', 'fl':0})
        path = edge.get_path(0, 'left')
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], {'type':'S', 'fl':0})
        

class TestShape(unittest.TestCase):
    def test_constructor(self):
        shape = Shape()
        self.assertEqual(shape.symbol, '')
        self.assertEqual(shape.name, '')
        self.assertEqual(shape.left, 0)
        self.assertEqual(shape.right, 0)
        self.assertEqual(shape.top, 0)
        self.assertEqual(shape.bottom, 0)
        self.assertEqual(shape.width, 0)
        self.assertEqual(shape.height, 0)
        self.assertEqual(len(shape.edges), 0)
        
        shape.right = 3
        self.assertEqual(shape.right, 3)
        self.assertEqual(shape.width, 3)

    def test_append(self):
        shape = Shape()
        edge = Edge()
        edge.add({'type':'S', 'fl':0})
        shape.append(edge)
        self.assertEqual(len(shape.edges), 1)

    def test_generate_name(self):
        shape = Shape()
        shape.symbol = 'hoge'
        self.assertEqual(shape.generate_name(), '31f30ddbcb1bf8446576f0e64aa4c88a9f055e3c')

if __name__ == '__main__':
    unittest.main()

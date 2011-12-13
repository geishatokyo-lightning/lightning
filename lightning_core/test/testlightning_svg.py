#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from lightning_core.lightning_svg import *

class TestLightningSvg(unittest.TestCase):
    def test_singleton(self):
        x1 = LightningSvg()
        x2 = LightningSvg()
        self.assertEqual(x1,x2)
        x1.hoge = 'fuga'
        self.assertEqual('fuga', x2.hoge)


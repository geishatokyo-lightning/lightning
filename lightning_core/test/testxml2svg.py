#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from lightning.lightning.lightning_svg import *
from lightning.lightning.databasemanager import *

class TestLightningSvg(unittest.TestCase):
    def test_singleton(self):
        x1 = LightningSvg()
        x2 = LightningSvg()
        self.assertEqual(x1,x2)
        x1.hoge = 'fuga'
        self.assertEqual('fuga', x2.hoge)

class TestDatabaseManager(unittest.TestCase):
    def test_singleton(self):
        x1 = DatabaseManager()
        x2 = DatabaseManager()
        self.assertEqual(x1,x2)
        x1.hoge = 'fuga'
        self.assertEqual('fuga', x2.hoge)

# -*- coding: utf-8 -*-

import queue
import unittest
from quickgui.framework.queues import NewLineQueue

class UnitCheckTest(unittest.TestCase):

        
    def test_strings_only(self):
        
        a = NewLineQueue()

        things = [1, None, (1,2), [3,4], slice, slice(1)]
        for thing in things:
            with self.assertRaises(TypeError):
                a.put(thing)

        # Does not raise
        a.put('str')

    def test_single_newline(self):
        
        a = NewLineQueue()
        a.put('pippo\n')
        
        assert a.get(block=False) == 'pippo\n'

    def test_newline_split(self):
        
        a = NewLineQueue()
        a.put('pippo\npluto\n')
        
        assert a.get(block=False) == 'pippo\n'
        assert a.get(block=False) == 'pluto\n'
        
    def test_composition(self):
        
        a = NewLineQueue()
        a.put('pippo')
        
        with self.assertRaises(queue.Empty):
            _ = a.get(block=False)
            
        a.put('\npluto')
        assert a.get(block=False) == 'pippo\n'

        with self.assertRaises(queue.Empty):
            _ = a.get(block=False)

        a.put('\npaperino\n')
        assert a.get(block=False) == 'pluto\n'
        assert a.get(block=False) == 'paperino\n'

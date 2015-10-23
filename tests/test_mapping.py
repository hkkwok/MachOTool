import unittest
from utils.mapping import Mapping


class TestMapping(unittest.TestCase):
    def test_mapping(self):
        map = Mapping()
        map[101] = 'bob'
        map[102] = 'john'
        map[103] = 'mary'
        map[104] = 'ellen'

        self.assertEqual('bob', map[101])
        self.assertEqual('john', map[102])
        self.assertEqual('mary', map[103])
        self.assertEqual('ellen', map[104])

        self.assertEqual('bob', map.value(101))
        self.assertEqual('john', map.value(102))
        self.assertEqual('mary', map.value(103))
        self.assertEqual('ellen', map.value(104))

        self.assertEqual(101, map.key('bob'))
        self.assertEqual(102, map.key('john'))
        self.assertEqual(103, map.key('mary'))
        self.assertEqual(104, map.key('ellen'))

        for k in (101, 102, 103, 104):
            self.assertTrue(map.has_key(k))

        for v in ('bob', 'john', 'mary', 'ellen'):
            self.assertTrue(map.has_value(v))

        self.assertItemsEqual([(101, 'bob'), (102, 'john'), (103, 'mary'), (104, 'ellen')], map.items())
        self.assertItemsEqual([101, 102, 103, 104], map.keys())
        self.assertItemsEqual(['bob', 'john', 'mary', 'ellen'], map.values())

        self.assertFalse(map.has_key(105))
        self.assertFalse(map.has_value('charles'))

        self.assertRaises(KeyError, lambda: map.value(105))
        self.assertRaises(KeyError, lambda: map.key('charles'))

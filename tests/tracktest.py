import unittest
from context import track

class TrackTest(unittest.TestCase):

    def test1_incorrect_path(self):
        
        with self.assertRaises(FileNotFoundError):
            obj = track.Track('blablabla')

    def test2_meta(self):
        obj = track.Track('test_track')
        self.assertEqual(obj.meta_info(), {'name': 'TEST TRACK',
                                           'length': 8.5,
                                           'type': '2',
                                           'location': 'Test City, Test Land'})
        

if __name__ == '__main__':
    unittest.main()

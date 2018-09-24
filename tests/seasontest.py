import unittest
from context import season

class SeasonTest(unittest.TestCase):

    def test1_metadata(self):
        obj = season.Season('Test_series.ini')
        #pprint(obj.meta_info())
        self.assertEqual(obj.meta_info(),
                        {'name': 'Test Series',
                         'year': '2018'})

    def test2_events(self):
        obj = season.Season('Test_series.ini')
        #pprint(obj.events_info())
        self.assertEqual(obj.schedule()[0],
                         {'date': '28/10',
                          'event_name': 'Richmond 400',
                          'no_of_laps': 400,
                          'track_directory': 'richmond_night'})

if __name__ == '__main__':
    unittest.main()

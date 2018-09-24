from context import results, season
from pprint import pprint
import unittest

class ResultsTest(unittest.TestCase):

    def test1(self):
        s = season.Season('Unipart Series.ini')
        r = results.Results('2x01_Richmond_R.html', s)
        self.assertEqual(r.event_id(), 0)
        pprint(r.Q_results())

if __name__ == '__main__':
    unittest.main()

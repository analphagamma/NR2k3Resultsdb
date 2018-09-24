import unittest
from pprint import pprint
from context import dbhandler

class DataBaseTest(unittest.TestCase):

    def test1_adding_full_season(self):
        dbobj = dbhandler.DBHandler('Unipart Series.ini')
        dbobj.reset_db(dbobj.db)
        dbobj.create_database()

        dbobj.enter_season_result('', 'Unipart Series.ini')

    @unittest.skip('')
    def test2_full_race_results(self):
        dbobj = dbhandler.DBHandler('Unipart Series.ini')
        pprint(dbobj.race_results('Toad Racers 250'))

    @unittest.skip('')
    def test3_driver_at_race(self):
        dbobj = dbhandler.DBHandler('Unipart Series.ini')
        pprint(dbobj.driver_in_race('T Striczki', 'Toad Racers 250'))



if __name__ == '__main__':
    unittest.main()

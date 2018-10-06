import unittest
from pprint import pprint
import webbrowser
from context import make_html as mh
from context import dbhandler
from pymongo import MongoClient

class htmlTest(unittest.TestCase):

    client = MongoClient('mongodb://localhost:27017/')
    client.server_info()
    db = client.chship
    dbobj = dbhandler.DBHandler('Unipart Series.ini')

    def test1_generate_everything(self):

        # define variables
        dr_stats = self.dbobj.all_drivers_history()
        s_info = self.dbobj.season_info()
        season_name = s_info['name']
        standings = self.dbobj.chship_standings()
        winners = self.dbobj.all_winners()

        # Generate Driver pages
        for dr in list(dr['name'] for dr in list(self.db.drivers.find())):
            driver_page = mh.DriverStats('Driver Info',
                                         [dr, ''],
                                         dr,
                                         dr_stats[dr])
            driver_page.create_page()
            
        # Generate Results pages (Events)
        for event in self.db.events.find():
            e_name = event['event_name']
            e_track = event['track_name']
            res = self.dbobj.race_results(e_name)
            results_page = mh.RaceResults('Race Results',
                                            [e_name, e_track],
                                            res,
                                            season_name,
                                            e_name)

            results_page.create_page()
        # Generate Track pages
        for tr in self.db.tracks.find():
            events_data = []
            tr_events = self.db.events.find({'track_name': tr['name']})
            for event in tr_events:
                events_data.append([event['event_id']+1,
                                    event['event_name'],
                                    winners[event['event_name']]['winner']
                                    ])
        
            track_page = mh.TrackPage('Track Info',
                                      [tr['name'], season_name],
                                      tr['name'],
                                      events_data)
            track_page.create_page()
            
        # Generate Season info page
        season_page =  mh.SeasonInfo('Season Info',
                                     [s_info['name'], s_info['year']],
                                     s_info,
                                     winners)
        season_page.create_page()
        
        # Generate Standings page
        standings_page = mh.StandingsPage('Standings',
                                          ['Official Standings', ''],
                                          standings,
                                          s_info)
        standings_page.create_page()

if __name__ == '__main__':
    unittest.main()

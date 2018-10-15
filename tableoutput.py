from pymongo import MongoClient
from modules.dbhandler import DBHandler
import modules.htmlcreator as hc
import webbrowser

class TableOutput:

    def __init__(self, series_ini):
        self.series_ini = series_ini
        client = MongoClient('mongodb://localhost:27017/')
        client.server_info()
        self.db = client.chship
        self.dbobj = DBHandler(series_ini)

    def generate_output(self):

        # define variables
        dr_stats = self.dbobj.all_drivers_history()
        s_info = self.dbobj.season_info()
        season_name = s_info['name']
        standings = self.dbobj.chship_standings()
        winners = self.dbobj.all_winners()
        next_event = self.dbobj.next_race()
        if not next_event:
            next_event = {'title': 'All events have been completed in this season.',
                          'name': '',
                          'track': ''
                        }
        else:
            next_event['title'] = 'Next event is:'

        # Generate Driver pages
        print('Generating Driver pages.')
        for dr in list(dr['name'] for dr in list(self.db.drivers.find())):
            driver_page = hc.DriverStats('Driver Info',
                                         [dr, ''],
                                         dr,
                                         dr_stats[dr])
            driver_page.create_page()
        print('Drivers done.')
            
        # Generate Results pages (Events)
        print('Generating Race pages.')
        for event in self.db.events.find():
            e_name = event['event_name']
            e_track = self.db.tracks.find_one({'track_directory': event['track_directory']})['name']
            res = self.dbobj.race_results(e_name)
            results_page = hc.RaceResults('Race Results',
                                            [e_name, e_track],
                                            res,
                                            season_name,
                                            e_name)

            results_page.create_page()
        print('Races done.')
        
        # Generate Track pages
        print('Generating Track pages.')
        for tr in self.db.tracks.find():
            events_data = []
            tr_events = self.db.events.find({'track_name': tr['name']})
            for event in tr_events:
                events_data.append([event['event_id']+1,
                                    event['event_name'],
                                    winners[event['event_name']]['winner']
                                    ])
        
            track_page = hc.TrackPage('Track Info',
                                      [tr['name'], season_name],
                                      tr['name'],
                                      events_data)
            track_page.create_page()
        print('Tracks done.')
        
        # Generate Season info page
        print('Generating Season Info.')
        season_page =  hc.SeasonInfo('Season Info',
                                     [s_info['name'], s_info['year']],
                                     s_info,
                                     winners)
        season_page.create_page()
        print('Season Info created.')
        
        # Generate Standings page
        print('Generating Standings.')
        next_ev = "{}\n{} at {}".format(next_event['title'],
                                        next_event['name'],
                                        next_event['track'])
        print(next_ev)
        
        standings_page = hc.StandingsPage('Standings',
                                          ['Official Standings', 'Season Info', next_ev],
                                          standings,
                                          s_info)
        standings_page.create_page()
        print('Standings created.')

        print('All pages created.\nOpening Standings in your default browser.')
        webbrowser.open_new('./tables/'+standings_page.filename+'.html')

if __name__ == '__main__':
    t_obj = TableOutput('Unipart Series.ini')
    t_obj.generate_output()


import os
from pymongo import MongoClient
from pprint import pprint

from modules.season import Season
from modules.results import Results
from modules.track import Track

class DBHandler:

    def __init__(self, series_ini):
        self.series_ini = series_ini # This object should be instantiated without the series_ini somehow.
        try:
            client = MongoClient('mongodb://localhost:27017/')
            client.server_info()
        except ServerSelectionTimeoutError:
            print('You\'re not connected to the MongoDB client.')
        else:
            print('Connecting to the MongoDB client...')
            self.db = client.chship
            print('Done.')

    ### DB INITIALISATION
    ### -----------------
    
    def reset_db(self, database):
        ''' Drops all tables from the database.

            USE WITH CARE!!
            This operation is irreversible. '''
            
        for col in database.list_collection_names():
            print('Dropping {}'.format(col))
            database[str(col)].drop()
        print('Done.')

    def create_database(self):
        ''' Sets up the season, events and tracks collections '''

        s = Season(self.series_ini)
        print('Creating Season table...')
        # insert season name and year
        self.db.season.insert_one(s.meta_info())
        print('Meta info added.')
        # insert event details //date, event name, number of laps, track directory//
        self.db.events.insert_many(s.schedule())
        print('Event list added.')
        # insert season id into current season's entries
        print('Creating Events table...')
        self.db.events.update_many({'event_name': {'$in': list(e['event_name'] for e in s.schedule())},
                                    'date': {'$in': list(e['date'] for e in s.schedule())}}, 
                                    {'$set': {'season_id': self.db.season.find_one({'name': s.meta_info()['name']})['_id']}})
        print('Events added.')

        # creating track table with the details of all tracks in the season
        print('Creating Tracks table...')
        for tr in s.tracktable():
            tr = tr.meta_info()
            self.db.tracks.update_one({'name': tr['name']},
                                      {'$setOnInsert': {'length': tr['length'],
                                                        'type': tr['type'],
                                                        'location': tr['location'],
                                                        'track_directory': tr['track_directory']}},
                                        upsert=True)
        print('Tracks added.')
        print('Initialisation finished.')

    ### DATA ENTRY
    ### ----------
    
    def enter_single_result(self, result_file, series_ini):
        r = Results(result_file, Season(series_ini)) # ADD CHECK IF SEASON EXISTS IN DB
        print('Adding:\n\tSeason: {}\n\tTrack: {}'.format(r.curSeason.meta_info()['name'], r.metadata()['track_name']))
        res = r.full_results()
        # create or update driverlist
        for dr in r.driverlist():
            self.db.drivers.update_one({'name': dr['name']},
                                  {'$setOnInsert': {'number': dr['number']}},
                                  upsert=True)
        # update event info with race conditions
        self.db.events.update_one({'event_id': r.event_id()}, {'$set': r.metadata()})
        # update event_id with _id object
        for row in res:
            row['event_id'] = self.db.events.find_one({'event_id': r.event_id()})['_id']
        # update driver name with _id object
        for row in res:
            row['driver'] = self.db.drivers.find_one({'name': row['driver']})['_id']
        # insert results
        self.db.results.insert_many(res)
        print('Done.')

    def enter_season_result(self, target_folder, series_ini):
        ''' iterates through all the html files in the ./exports_imports/target_folder '''
        print('Looking in folder {}...'.format(target_folder))
        for f in os.walk('../exports_imports/'+target_folder): # ADD CHECK!!
            results_files = f[2]
            print('{} exported results found'.format(len(results_files)))
        for rf in results_files:
            self.enter_single_result(rf, series_ini)
        print('All entries added.')

    ### QUERIES
    ### -------

    def chship_standings(self):
        pass

    def race_results(self, race_name):
        ''' Returns a race's full results
            sorted by position '''
        event = self.db.events.find_one({'event_name': race_name})
        if event == None:
            print('Event "{}" not found in season'.format(race_name))
            return None
        full_results = []
        for r in self.db.results.find({'event_id': event['_id']}):
            result_row = {'#': r['#'],
                          'driver': self.db.drivers.find_one({'_id': r['driver']})['name'],
                          'interval': r['interval'] ,
                          'laps': r['laps'],
                          'laps_led': r['laps_led'],
                          'most_led': r['most_led'],
                          'points': r['points'],
                          'q_position': r['q_position'],
                          'q_time': r['q_time'],
                          'r_position': r['r_position'],
                          'status': r['status']
                          }
            full_results.append(result_row)

        return sorted(full_results, key=lambda k: k['r_position'])
        
    def all_winners(self):
        ''' Returns a list of tuples where

            tuple[0] is the event name
            tuple[1] is the driver's name. '''
            
        def winner_of_race(self, race_name):
            ''' Returns an object from self.db.drivers. '''
            
            winner = self.db.results.find_one({'event_id': self.db.events.find_one({'event_name': race_name})['_id'],
                                               'r_position': {'$eq': 1}
                                               })
            return db.drivers.find_one({'_id': winner['driver']})

        all_winners = []
        for event in self.db.events.find():
            all_winners.append((event['event_name'], winner_of_race(event['event_name'])['name']))

        return all_winners
            
    def top_10_of_race(self, race_name):
        ''' Returns a list of tuples of the top 10 finishing drivers
            from the input race

            tuple[0] is the finishing position
            tuple[1] is the driver's name '''
            
        all_top10 = []
        top10 = self.db.results.find({'event_id': self.db.events.find_one({'event_name': race_name})['_id'],
                                      'r_position': {'$lte': 10}
                                      })
        
        for dr in top10:
            all_top10.append((dr['r_position'], self.db.drivers.find_one({'_id': dr['driver']})['name']))

        return sorted(all_top10, key=lambda k: k[0])
    

    def driver_summary(self, driver_name):
        ''' Returns:
                points
                wins
                top5
                top10
                pole_positions
                avg_finish
                avg_qualifying
                laps_led
                dnf
                races'''
        pass

    def driver_in_race(self, driver_name, race_name):
        race = self.db.events.find_one({'event_name': race_name})
        if race == None:
            print('Event "{}" not in season'.format(race_name))
            return None
        driver = self.db.drivers.find_one({'name': driver_name})
        if driver == None:
            print('Driver "{}" not in season'.format(driver_name))
            return None
    
        results = self.db.results.find_one({'event_id': race['_id'], 'driver': driver['_id']})
        results['driver'] = self.db.drivers.find_one({'_id': results['driver']})['name']
        results['event_id'] = self.db.events.find_one({'_id': results['event_id']})['event_name']
        return results

    def driver_on_track_type(self, driver_name, track_type):
        pass

    

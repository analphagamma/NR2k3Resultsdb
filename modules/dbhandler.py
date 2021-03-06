import os
from pymongo import MongoClient
from pprint import pprint

from modules.season import Season
from modules.results import Results
from modules.track import Track

class DBHandler:
    ''' All MongoDB operations.
        It initializes the database and runs all queries. '''
        
    def __init__(self, series_ini):
        self.series_ini = series_ini
        self.season = Season(self.series_ini)
        try:
            client = MongoClient('mongodb://localhost:27017/')
            client.server_info()
        except ServerSelectionTimeoutError:
            print('You\'re not connected to the MongoDB client.')
        else:
            print('Connecting to the MongoDB client...')
            self.db = client.chship
            print('Done.')
            try:
                self.season_id = self.db.season.find_one(self.season.meta_info())['_id']
            except TypeError:
                self.season_id = None
            print(self.season_id)

        self.point_system = 'default'

    ### DB INITIALISATION
    ### -----------------
    
    def reset_db(self):
        ''' Drops all collections from the database.

            USE WITH CARE!!
            This operation is irreversible. '''
            
        for col in self.db.list_collection_names():
            print('Dropping {}'.format(col))
            self.db[str(col)].drop()
        print('Done.')

    def create_database(self):
        ''' Sets up the season, events and tracks collections '''

        if self.db.season.find_one(self.season.meta_info()):
            print('Season already in database\nUse the option 2 in the main menu to add results.')
            return
        print('Creating Season table...')
        # insert season name and year merged with season number
        self.db.season.insert_one(self.season.meta_info())
        print('Meta info added.')
        # insert event details //date, event name, number of laps, track directory//
        self.db.events.insert_many(self.season.schedule())
        print('Event list added.')
        # insert season id into current season's entries
        print('Creating Events table...')
        self.season_id = self.db.season.find_one(self.season.meta_info())['_id']
        self.db.events.update_many({'event_name': {'$in': list(e['event_name'] for e in self.season.schedule())},
                                    'date': {'$in': list(e['date'] for e in self.season.schedule())}}, 
                                    {'$set': {'season_id': self.season_id}
                                    }
                                  )
        print('Events added.')

        # creating track table with the details of all tracks in the season
        print('Creating Tracks table...')
        for tr in self.season.tracktable():
            tr = tr.meta_info()
            self.db.tracks.update_one({'track_directory': tr['track_directory']},
                                      {'$setOnInsert': {'length': tr['length'],
                                                        'type': tr['type'],
                                                        'location': tr['location'],
                                                        'name': tr['name']}},
                                        upsert=True)
        print('Tracks added.')
        print('Initialisation finished.')

    ### DATA ENTRY
    ### ----------
    
    def enter_single_result(self, result_file):
        ''' Adds a race's result from the exported html file. '''
        
        r = Results(result_file, self.season, self.point_system)
        
        cur_event = self.db.events.find_one({'event_id': r.event_id(), 'date': r.metadata()['date']})
        if not cur_event:
            return
        elif len(cur_event.items()) != 7:
            print('Results for {} already in database.'.format(cur_event['event_name']))
            return
            
        print('Adding:\n\tSeason: {}\n\tYear: {}\n\tTrack: {}'.format(r.curSeason.meta_info()['name'],
                                                                      r.curSeason.meta_info()['year'],
                                                                      r.metadata()['track_name']))
        res = r.full_results()
        # create or update driverlist
        for dr in r.driverlist():
            self.db.drivers.update_one({'name': dr['name']},
                                      {'$setOnInsert': {'number': dr['number']}},
                                      upsert=True)
        # update event info with race conditions
        self.db.events.update_one({'event_id': r.event_id(),
                                   'date': r.metadata()['date']},
                                        {'$set': r.metadata()}
                                 )
        # update event_id with _id object, driver with driver_id, and adding season_id
        for row in res:
            row['event_id'] = self.db.events.find_one({'event_id': r.event_id()})['_id']
            row['driver'] = self.db.drivers.find_one({'name': row['driver']})['_id']
            row['season_id'] = self.season_id
        # insert results
        self.db.results.insert_many(res)
        print('Done.')

    def enter_season_result(self, target_folder=''):
        ''' iterates through all the html files in the ./exports_imports/target_folder '''

        # check if season exists in database
        if not self.db.season.find_one(self.season.meta_info()):
            self.create_database()
        print('Looking in folder {}...'.format(target_folder))
        for f in os.walk('./exports_imports/'+target_folder): # ADD CHECK!!
            results_files = f[2]
            print('{} exported results found'.format(len(results_files)))
        for rf in results_files:
            self.enter_single_result('/'.join([target_folder, rf]))
        print('All entries added.')

    ### QUERIES
    ### -------

    ### Season queries
    def chship_standings(self):
        standings = []
        for driver in self.db.drivers.find():
            standings.append([driver['name'], *self.driver_summary(driver['name'])])
        return sorted(standings, key=lambda k: k[1], reverse=True)

    def season_info(self):
        ''' Returns the season's name, year and a list of the events with their metadata. '''

        s_info = self.season.meta_info()
        return {'name': s_info['name'],
                'year': s_info['year'],
                'event_list': self.season.schedule()}

    ### Race queries
    def race_results(self, race_name):
        ''' Returns a race's full results
            sorted by position '''
            
        event = self.db.events.find_one({'event_name': race_name,
                                         'season_id': self.season_id})
        if event == None:
            print('Event "{}" not found in season'.format(race_name))
            return None
        full_results = []
        for r in self.db.results.find({'event_id': event['_id']}):
            result_row = {'#': r['#'],
                          'driver': self.db.drivers.find_one({'_id': r['driver']})['name'],
                          'interval': r.get('interval'),
                          'laps': r.get('laps'),
                          'laps_led': r.get('laps_led'),
                          'most_led': r.get('most_led'),
                          'points': r.get('points'),
                          'q_position': r.get('q_position'),
                          'q_time': round(r.get('q_time'), 3),
                          'r_position': r.get('r_position'),
                          'status': r.get('status')
                          }
            if not result_row['r_position']:
                result_row['r_position'] = 99
            full_results.append(result_row)

        return sorted(full_results, key=lambda k: k['r_position'])

    ### Driver queries    
    def all_winners(self):
        ''' Returns a list of tuples where

            tuple[0] is the event name
            tuple[1] is the driver's name. '''
            
        def winner_of_race(self, race_name, season):
            ''' Returns an object from self.db.drivers. '''
            
            winner = self.db.results.find_one({'event_id': self.db.events.find_one({'event_name': race_name})['_id'],
                                               'season_id': season,
                                               'r_position': {'$eq': 1}
                                               })

            trackd = self.db.events.find_one({'event_name': race_name})['track_directory']
            if not winner:
                return {'winner': '-',
                        'track': self.db.tracks.find_one({'track_directory': trackd})['name'],
                        'track_directory': trackd}
            else:
                return {'winner':self.db.drivers.find_one({'_id': winner['driver']})['name'],
                        'track': self.db.tracks.find_one({'track_directory': trackd})['name'],
                        'track_directory': trackd}

        all_winners = {}
        for event in self.db.events.find():
            all_winners[event['event_name']] = winner_of_race(self, event['event_name'], self.season_id)
        return all_winners

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

        dr_id = self.db.drivers.find_one({'name': driver_name})['_id']
        
        def points():
            ''' Returns the aggregate points of a driver. '''
            points = self.db.results.aggregate([{'$match':
                                                    {'driver': dr_id,
                                                     'season_id': self.season_id}
                                                },
                                                {'$group':
                                                    {'_id': 'null',
                                                     'points': 
                                                        {'$sum': '$points'}
                                                    }
                                                }])
            if points.alive:
                return points.next()['points']
            else:
                return 0
                                         
        def wins():
            ''' Returns the number of topfives by a driver. '''
            wins = self.db.results.aggregate([{'$match':
                                                 {'driver': dr_id,
                                                  'r_position': 1,
                                                  'season_id': self.season_id}
                                                },
                                            {'$count': 'wins'}
                                            ])
            if wins.alive:
                return wins.next()['wins']
            else:
                return 0
                                                                  
        def top5s():
            ''' Returns the number of top5 finishes by a driver. '''
            topfives =  self.db.results.aggregate([{'$match':
                                                         {'driver': dr_id,
                                                         'r_position': {'$lte': 5},
                                                         'season_id': self.season_id}
                                                      },
                                                     {'$count': 'topfives'}
                                                      ])
            if topfives.alive:
                return topfives.next()['topfives']
            else:
                return 0
                                          
        def top10s():
            ''' Returns the number of top10 finishes by a driver. '''
            toptens =  self.db.results.aggregate([{'$match':
                                                     {'driver': dr_id,
                                                     'r_position': {'$lte': 10},
                                                     'season_id': self.season_id}
                                                    },
                                                    {'$count': 'toptens'}
                                                    ])
            if toptens.alive:
                return toptens.next()['toptens']
            else:
                return 0
            
        def pole_pos():
            ''' Returns the number of pole positions by a driver. '''
            poles =  self.db.results.aggregate([{'$match':
                                                    {'driver': dr_id,
                                                     'q_position': 1,
                                                     'season_id': self.season_id}
                                                },
                                                {'$count': 'poles'}
                                                ])
            if poles.alive:
                return poles.next()['poles']
            else:
                return 0
        
        def avg_finish():
            ''' Returns the average finishing position of a driver. '''
            avg_fin =  self.db.results.aggregate([{'$match':
                                                {'driver': dr_id,
                                                 'season_id': self.season_id}
                                                 },
                                                 {'$group':
                                                    {'_id': 'null',
                                                     'avg': 
                                                        {'$avg': '$r_position'}
                                                    }
                                                 }])
            if avg_fin.alive:
                return avg_fin.next()['avg']
            else:
                return 0
            
        def avg_start():
            ''' Returns the average starting position of a driver. '''
            avg_st =  self.db.results.aggregate([{'$match':
                                                {'driver': dr_id,
                                                 'season_id': self.season_id}
                                                 },
                                                {'$group':
                                                    {'_id': 'null',
                                                     'avg': 
                                                        {'$avg': '$q_position'}
                                                    }
                                                }])
            if avg_st.alive:
                return avg_st.next()['avg']
            else:
                return 0
            
        def laps_led():
            ''' Returns the number of laps led by a driver. '''
            led =  self.db.results.aggregate([{'$match':
                                                {'driver': dr_id,
                                                 'season_id': self.season_id
                                                 }
                                              },
                                             {'$group':
                                                {'_id': 'null',
                                                 'led': 
                                                    {'$sum': '$laps_led'}
                                                }
                                              }])
            if led.alive:
                return led.next()['led']
            else:
                return 0
            
        def dnfs():
            ''' Returns the number of retires of a driver. '''
            dnf = self.db.results.aggregate([{'$match':
                                                {'driver': dr_id,
                                                 'status': {'$ne': 'Running'},
                                                 'season_id': self.season_id
                                                }
                                            },
                                            {'$count': 'dnf'}                                  
                                            ])
            if dnf.alive:
                return dnf.next()['dnf']
            else:
                return 0
            
        def num_races():
            ''' Returns the number of races started by the driver. '''
            races = self.db.results.aggregate([{'$match':
                                                     {'driver': dr_id,
                                                     'season_id': self.season_id
                                                     }
                                                 },
                                                 {'$count': 'races'}                                  
                                                 ])
            if races.alive:
                return races.next()['races']
            else:
                return 0

        return (points(),
                wins(),
                top5s(), 
                top10s(),
                pole_pos(),
                round(avg_finish(), 1),
                round(avg_start(),1),
                laps_led(),
                dnfs(),
                num_races()
                )

    def driver_in_races(self, driver_name):
        ''' Returns all the event collections that the driver was part of.
            This method returns a generator object. '''
        dr_id = self.db.drivers.find_one({'name': driver_name})['_id']
        
        res_cur = self.db.results.find({'driver': dr_id, 'season_id': self.season_id})
        for events in res_cur:
            yield events

    def all_drivers_history(self):
        ''' Returns all drivers' results summary from every event they took part in. '''

        all_drivers = {}

        for driver in self.db.drivers.find():
            dr_results = []
            for ev in self.driver_in_races(driver['name']):
                event = self.db.events.find_one({'_id': ev['event_id']})
                dr_results.append([event['event_id']+1,
                                   event['event_name'],
                                   event['track_name'],
                                   ev.get('r_position'),
                                   ev['q_position'],
                                   ev.get('laps_led'),
                                   ev.get('most_led'),
                                   ev.get('status')])
            all_drivers[driver['name']] = sorted(dr_results, key=lambda k: k[0])

        return all_drivers

    def next_race(self):
        ''' Returns the next event's name and track location
            without results data in the current season. '''

        next_ev = {}
        for ev in self.db.events.find({'season_id': self.season_id}):
            if not self.db.results.find_one({'event_id': ev['_id']}):
                if next_ev == {} or ev['event_id'] < next_ev['event_id']:
                    next_ev = ev 
        if not next_ev:
            return None
        else:
            return {'name': next_ev['event_name'],
                    'track': self.db.tracks.find_one({'track_directory': next_ev['track_directory']})['name']}

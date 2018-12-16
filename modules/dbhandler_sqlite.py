import sqlite3
from pprint import pprint

from modules.season import Season
from modules.results import Results
from modules.track import Track

class DBHandler:
    ''' All database operations.
        It initializes the database and runs all queries. '''

    def __init__(self, series_ini, database):
        self.series_ini = series_ini
        self.database = database
        self.season = Season(self.series_ini)
        self.point_system = 'default'
        
        self.conn = sqlite3.connect(self.database)
        self.c = self.conn.cursor()
        # get season_id


    ### DB INITIALISATION
    ### -----------------

    def reset_db(self):
        ''' Drops all tables from the database.
            For testing purposes.

            USE WITH CARE!!
            This operation is irreversible. '''

        self.c.execute('''DELETE FROM Seasons;''')
        print("All records from Seasons deleted.")
        self.c.execute('''DELETE FROM Events;''')
        print("All records from Events deleted.")
        self.c.execute('''DELETE FROM Drivers;''')
        print("All records from Drivers deleted.")
        self.c.execute('''DELETE FROM Tracks;''')
        print("All records from Tracks deleted.")
        self.conn.commit()
        print("Purge completed.")

    def create_database(self):
        ''' Sets up the season, events and tracks collections '''
        season_meta = self.season.meta_info()
        # check if season is already in the create_database
        query = '''SELECT
                        *
                   FROM Seasons
                   WHERE name=?
                   AND year=?;'''
        self.c.execute(query, (season_meta['name'], season_meta['year']))
        if self.c.fetchone():
            print('This season is already in the database\nPlease use option 2 from the main menu.')
            return
        # insert season name and year merged with season number
        query = '''INSERT INTO Seasons(name,
                                       year)
                        VALUES (?, ?);'''
        self.c.execute(query, (season_meta['name'], season_meta['year']))
        print('Season info added.')
        # get season_id
        query = '''SELECT DISTINCT
                        id
                   FROM Seasons
                   WHERE name=?
                   AND year=?;'''
        self.c.execute(query, (season_meta['name'], season_meta['year']))
        s_id = self.c.fetchone()
        # insert event details //date, event name, number of laps, track directory//
        query = '''INSERT INTO Events(date,
                                      name,
                                      no_of_laps,
                                      track_directory,
                                      season_id)
                    VALUES (?, ?, ?, ?, ?);'''
        for ev in self.season.schedule():
            self.c.execute(query, (ev['date'], ev['event_name'], ev['no_of_laps'], ev['track_directory'], s_id[0]))
        print('Events added.')
        # creating track table with the details of all tracks in the season
        query = '''INSERT OR IGNORE INTO Tracks(name,
                                                track_directory,
                                                length,
                                                type,
                                                location)
                    VALUES (?, ?, ?, ?, ?);'''
        for tr in self.season.tracktable():
            tr = tr.meta_info()
            self.c.execute(query, (tr['name'], tr['track_directory'], tr['length'], tr['type'], tr['location']))
        print('Tracks added.')
        self.conn.commit()
        
    ### DATA ENTRY
    ### ----------

    def enter_single_result(self, result_file):
        ''' Adds a race's result from the exported html file. '''

        r = Result(result_file, self.season, self.point_system)
        res = r.full_results()
        meta = r.metadata()
        # check if event exists and if it does check if it already has results
        query = '''SELECT
                        *
                   FROM Events
                   WHERE id = ?
                   AND date = ?;'''
        c.execute(query, r.event_id(), meta['date'])
        cur_event = c.fetchone()
        if not cur_event:
            return
        elif len(cur_event.items()) != 7:
            print('Results for {} already in database.'.format(cur_event['event_name']))
            return
        # create or update driverlist
        for dr in r.driverlist():
            query = '''INSERT OR INGORE INTO Drivers(name,
                                                     number)
                            VALUES (?, ?)'''
        # update event info with race conditions
        query = '''UPDATE Events
                   SET name = ?,
                       no_of_laps = ?,
                       track_directory = ?,
                       season_id = ?
                   WHERE id = ?
                   AND date = ?;'''
        c.execute(query,
                  meta['name'],
                  meta['no_of_laps'],
                  meta['track_directory'],
                  meta['season_id'],
                  r.event_id(),
                  meta['date'])
        # update event_id with _id object, driver with driver_id, and adding season_id

        # insert results
        print('Adding:\n\tSeason: {}\n\tYear: {}\n\tTrack: {}'.format(r.curSeason.meta_info()['name'],
                                                                      r.curSeason.meta_info()['year'],
                                                                      r.metadata()['track_name']))
        

    def enter_season_result(self, target_folder=''):
        ''' iterates through all the html files in the ./exports_imports/target_folder '''

        # check if season exists in database
        pass

    ### QUERIES
    ### -------

    ### Season queries
    def chship_standings(self):
        ''' Returns the standings table '''
        pass

    def season_info(self):
        ''' Returns the season's name, year and a list of the events with their metadata. '''

        pass

    ### Race queries
    def race_results(self, race_name):
        ''' Returns a race's full results
            sorted by position '''

        pass

    ### Driver queries
    def all_winners(self):
        ''' Returns a list of tuples where

            tuple[0] is the event name
            tuple[1] is the driver's name. '''

        def winner_of_race(self, race_name, season):
            ''' Returns an object from self.db.drivers. '''

            pass

        pass

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


        def points():
            ''' Returns the aggregate points of a driver. '''
            pass

        def wins():
            ''' Returns the number of topfives by a driver. '''
            pass

        def top5s():
            ''' Returns the number of top5 finishes by a driver. '''
            pass

        def top10s():
            ''' Returns the number of top10 finishes by a driver. '''
            pass

        def pole_pos():
            ''' Returns the number of pole positions by a driver. '''
            pass

        def avg_finish():
            ''' Returns the average finishing position of a driver. '''
            pass

        def avg_start():
            ''' Returns the average starting position of a driver. '''
            pass

        def laps_led():
            ''' Returns the number of laps led by a driver. '''
            pass

        def dnfs():
            ''' Returns the number of retires of a driver. '''
            pass

        def num_races():
            ''' Returns the number of races started by the driver. '''
            pass

        pass

    def driver_in_races(self, driver_name):
        ''' Returns all the event collections that the driver was part of.
            This method returns a generator object. '''
        pass

    def all_drivers_history(self):
        ''' Returns all drivers' results summary from every event they took part in. '''

        pass

    def next_race(self):
        ''' Returns the next event's name and track location
            without results data in the current season. '''

        pass

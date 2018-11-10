from bs4 import BeautifulSoup
from pprint import pprint
from configparser import ConfigParser
import re
import os
from modules.season import Season

class Results:
    ''' The class that extracts and organises data from the exported html. '''
    
    def __init__(self, exported_results, curSeason: Season, point_system):
        self.exported_results = exported_results
        print('Reading ', self.exported_results)
        # checking the validity of the file
        if not os.path.isfile('./exports_imports/' + self.exported_results):
            raise FileNotFoundError('File doesn\'t exist or path is incorrect')

        # open result file and prepare it for parsing
        with open('./exports_imports/' + self.exported_results, 'rb') as f:
            self.soup = BeautifulSoup(f, 'html.parser')

        # the season object    
        self.curSeason = curSeason

        # importing point system from the point_system.ini file
        self.point_system = point_system
        p_ini = ConfigParser()
        p_ini.read('point_system.ini') # we assume it's present and in the correct format
        if point_system not in p_ini.sections():
            point_system = 'default' # in case of incorrect input we use the default point system
        self.point_table = {} # we store the points in a dict
        for pos in p_ini[point_system]:
            self.point_table[pos] = int(p_ini[point_system][pos])
    
    def make_tuples(self, seq: list, ch: int):
        ''' Groups list elements into tuples.
            The original data is in a table and BS lists every single value
            separately, so they need to be grouped by row.
            
            seq: the list
            ch: number of elements in each group. '''
            
        seqt = []
        for v in seq:
            seqt.append(v.get_text().strip('\r\n\t'))
        return [seqt[i:i + ch] for i in range(0, len(seqt), ch)]
        
    def metadata(self):
        ''' Extracts race data and returns it in a dictionary. '''
        
        meta = self.soup.findAll('h3')

        track = meta[0].get_text().strip()[7:]
        date = meta[1].get_text().strip()[6:].split('/')
        weather_Q = meta[3].get_text().strip()[9:]
        yellows = meta[6].get_text().strip()
        lead_ch = meta[7].get_text().strip()
        weather_R = meta[8].get_text().strip()[9:]

        yellow_flags = int(re.findall('\d+(?=\s+\()', yellows)[0]) # nice
        yellow_laps = int(re.findall('(?<=\()\d+', yellows)[0])

        lead_changes = int(re.findall('\d+(?=\s+\()', lead_ch)[0])
        leaders = int(re.findall('(?<=\()\d+', lead_ch)[0])

        return {'track_name': re.sub('[^a-zA-Z0-9\'_]+', ' ', track).strip().title(),
                'date': '-'.join(['20'+date[2], date[0], date[1]]),
                'q_weather': weather_Q, # we'll store weather as a string for now
                'r_weather': weather_R,
                'yellow_flags': yellow_flags,
                'yellow_laps': yellow_laps,
                'lead_changes': lead_changes,
                'leaders': leaders}

    def event_id(self):
        ''' Searches the event list and tries to match the date of the race.
            Returns an integer. '''
            
        for event in self.curSeason.schedule():
            if event['date'] == self.metadata()['date']:
                return event['event_id']
        print('Race at {} on {} is not scheduled in this season.'.format(self.metadata()['track_name'],
                                                                        str(self.metadata()['date']).split()[0]))
        return None
        
    def Q_results(self):
        ''' Extracts the results from Qualifying and returns the values
            as a list of dictionaries.

            Finishing position is returned as an int,
            qualifying time is returned as a float. '''
            
        Q_data = self.soup.findAll('table')[0]
        event_id = self.event_id()
        if event_id == None:
            return None
        results = []
        for line in self.make_tuples(Q_data.findAll('td'), 4)[1:-1]:
            # time must be converted to seconds if it's over a minute
            minutes = re.findall('\d+(?=:)', line[3])[0] if re.match('\d+(?=:)', line[3]) else 0
            seconds = re.findall('(?<=:).+', line[3])[0] if re.match('\d+(?=:)', line[3]) else line[3]
            q_time = int(minutes)*60 + float(seconds)
            
            pos_data = {'event_id': self.event_id(),
                        'q_position': int(line[0]),
                        '#': line[1],
                        'driver': line[2],
                        'q_time': q_time}
            results.append(pos_data)
        if results == []:
            print('No Qualifying data for {}'.format(self.metadata()['track_name']))

        return results

    def R_results(self):
        ''' Extracts the results from the Race and returns the values in
            list of dictionaries.

            Finishing position, number of laps completed, number of
            points received and the number of laps led are integers,
            most laps led in a boolean. '''
            
        R_data = self.soup.findAll('table')[1]
        R_data_tuples = self.make_tuples(R_data.findAll('td'), 9)[1:] # we group them by rows

        # check if partial_points are used and if there are less than 42 drivers
        if self.point_table.get('partial_points') == 1 and len(R_data_tuples) != 42:
            # points are proportianally reduced so that last position gets 1 point.
            point_modifier = self.point_table.get(str(len(R_data_tuples) + 1))            
        else:
            point_modifier = 0
            
        results = []
        for line in R_data_tuples:
            # get points from point_system.ini
            points = self.point_table.get(line[0]) - point_modifier
            if points == None:
                points = 0 # if there are no entries for that position
                
            if line[6][-1] == '*': # most laps led is indicated by an asterisk in the game
                laps_led = int(line[6].strip('*'))
                most_led = True
                points += self.point_table.get('most_led') + self.point_table.get('laps_led')
            else:
                laps_led = int(line[6])
                if laps_led > 0:
                    points += self.point_table.get('laps_led')
                most_led = False
                
            pos_data = {'r_position': int(line[0]),
                        '#': line[2],
                        'driver': line[3],
                        'interval': line[4],
                        'laps': int(line[5]),
                        'points': points,
                        'status': line[8]}
            
            pos_data['laps_led'] = laps_led
            pos_data['most_led'] = most_led
            
            results.append(pos_data)
        if results == []:
            print('No Race data for {}'.format(self.metadata()['track_name']))

        return results

    def full_results(self):
        ''' Joins the two result lists'''
        
        merged = {}
        Q = self.Q_results()
        R = self.R_results()
        try:
            Q+R
        except TypeError:
            print('Could not read results.')
            return None
        else:
            for item in Q+R:
                if item['#'] in merged:
                    merged[item['#']].update(item)
                else:
                    merged[item['#']] = item

            return [val for (_, val) in merged.items()]

    def driverlist(self):
        ''' Creates a list of drivers who ran this race. '''
        
        driverlist = []
        for dr in self.full_results():
            driverlist.append({'name': dr['driver'], 'number': dr['#']})

        return driverlist

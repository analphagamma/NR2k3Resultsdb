import configparser
import sys, os
from modules.track import Track

class Season:
    ''' Provides data for the Season table. It initializes by
        opening and parsing the series ini file. '''
        
    def __init__(self, ini_file):
        self.ini_file = './series/cup/' + ini_file
        if not os.path.isfile('./series/cup/' + ini_file):
            raise FileNotFoundError('Ini file doesn\'t exist or path is incorrect')

        self.config = configparser.ConfigParser(inline_comment_prefixes=';')
        try:
            self.config.read(self.ini_file)
        except UnicodeDecodeError:
            self.config.read(self.ini_file, encoding='Latin-1')
        except:
            print('There is a problem with the ini file.')
            sys.exit(1)

        if self.config.sections() != []:
            print('Ini file read successfully.')
        else:
            print('Couldn\'t open ini file')

    def meta_info(self):
        ''' Returns the season's name and year in a dict. '''
        return {'name': self.config[' Season ']['name'],
                'year': self.config[' Season ']['year']}

    def schedule(self):
        ''' Gets each individual event's date, name, number of laps and
            track directory (that will be used to get further information
            on the track)
            Returns a list of dictionaries. '''
        sch = []
        for i, sec in enumerate(self.config.sections()):
            if sec == ' Season ': # when the loop reaches the next section
                return sch
            else:
                day = self.config[sec]['day'].strip(' \t')
                if len(day) == 1:
                    day = '0'+day
                month = self.config[sec]['month'].strip(' \t')
                if len(month) == 1:
                    month = '0'+month
                event_name = self.config[sec]['name'].strip(' \t')
                no_of_laps = self.config[sec]['numberOfLaps'].strip(' \t')
                track_directory = self.config[sec]['trackDirectory'].strip(' \t')
                
                sch.append({'event_id': i,
                            'date': '-'.join([self.meta_info()['year'], month, day]),
                            'event_name': event_name,
                            'no_of_laps': int(no_of_laps),
                            'track_directory': track_directory})

    def tracktable(self):
        ''' Creates a list of tracks used in the season.
            Returns a set to avoid duplicates'''
        tracklist = []
        for tr in self.schedule():
            tracklist.append(Track(tr['track_directory']))

        return tracklist

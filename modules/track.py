import configparser
import sys, os
import re

class Track:

    def __init__(self, track_dir):
        self.track_dir = track_dir
        if not os.path.exists('./tracks/{}'.format(self.track_dir)):
            raise FileNotFoundError

        self.config = configparser.ConfigParser(inline_comment_prefixes=';')
        try:
            self.config.read('./tracks/{}/track.ini'.format(self.track_dir))
        except UnicodeDecodeError:
            self.config.read('./tracks/{}/track.ini'.format(self.track_dir), encoding='Latin-1')
        except:
            print('There is a problem with the ini file.')
            sys.exit(1)

    def meta_info(self):
        ''' Extracts track information from the track.ini '''
        
        return {'name': re.sub('[^a-zA-Z0-9\'_]+', ' ', self.config[' track ']['track_name']).strip().title(),
                'length': float(self.config[' track ']['track_length'].strip('m ')),
                'type': self.config[' track ']['track_type'],
                'location': '{}, {}'.format(self.config[' track ']['track_city'], self.config[' track ']['track_state']),
                'track_directory': self.track_dir}

    def __str__(self):
        return self.meta_info()['name']

    def __eq__(self, other):
        if self.track_dir == other.track_dir:
            return True
        else:
            return False

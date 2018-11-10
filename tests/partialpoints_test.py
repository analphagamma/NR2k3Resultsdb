import unittest
from bs4 import BeautifulSoup
from configparser import ConfigParser
from pprint import pprint

class mockResults():

    def __init__(self, exported_results, point_system):
        self.exported_results = exported_results
        with open('./exports_imports/' + self.exported_results, 'rb') as f:
            self.soup = BeautifulSoup(f, 'html.parser')

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

    def R_results(self):
        ''' Extracts the results from the Race and returns the values in
            list of dictionaries.

            Finishing position, number of laps completed, number of
            points received and the number of laps led are integers,
            most laps led in a boolean. '''
            
        R_data = self.soup.findAll('table')[1]
        R_data_tuples = self.make_tuples(R_data.findAll('td'), 9)[1:]
        if self.point_table.get('partial_points') == 1:
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

class TestmockResults(unittest.TestCase):

    def test1_lastposition(self):
        obj = mockResults('Richmond.html', 'modern')
        self.assertEqual(obj.R_results()[-1]['points'], 1)    

if __name__ == '__main__':
    unittest.main()

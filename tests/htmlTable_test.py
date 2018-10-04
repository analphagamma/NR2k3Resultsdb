import unittest
from pprint import pprint
import webbrowser
from context import make_html as mh
from context import dbhandler
from pymongo import MongoClient

class TableTest(unittest.TestCase):

    client = MongoClient('mongodb://localhost:27017/')
    client.server_info()
    db = client.chship
    dbobj = dbhandler.DBHandler('Unipart Series.ini')

    @unittest.skip('')
    def test1_build_table(self):

        widths = [18,18,65,18,140,65,45,45,60,50,50]
        tabledata = [
                      ['P',
                       'S',
                       'Q Time',
                       '#',
                       'Name',
                       'Interval',
                       'Laps',
                       'Led',
                       'Led Most',
                       'Points',
                       'Status'],
                       ['1',
                        '1',
                        '1:55.456',
                        '00',
                        'I Mitchell \'Mitch\'',
                        '189.901',
                        '500',
                        '67',
                        'True',
                        '200',
                        'Running'],
                       ['2',
                        '3',
                        '1:54.456',
                        '10',
                        'Peter PooPoo',
                        '-23.2',
                        '500',
                        '60',
                        'False',
                        '180',
                        'Running']
                    ]

        
        h = mh.htmlTable(tabledata, widths)
        t_col = h.tcolour('black', '#d3d3d3')
        t_name = h.tname('Results')
        html = h.assemble(t_name, t_col)
        
        with open('table_test.html', 'w') as html_f:
            html_f.write(html)
        #webbrowser.open('table_test.html')

    @unittest.skip('')
    def test2_generate_whole_page(self):

        widths = [18,18,65,18,140,65,45,45,60,50,50]
        tabledata = [
                      ['P',
                       'S',
                       'Q Time',
                       '#',
                       'Name',
                       'Interval',
                       'Laps',
                       'Led',
                       'Led Most',
                       'Points',
                       'Status',],
                       ['1',
                        '1',
                        '1:55.456',
                        '00',
                        'I Mitchell \'Mitch\'',
                        '189.901',
                        '500',
                        '67',
                        'True',
                        '200',
                        'Running'],
                       ['2',
                        '3',
                        '1:54.456',
                        '10',
                        'Peter PooPoo',
                        '-23.2',
                        '500',
                        '60',
                        'False',
                        '180',
                        'Running']
                    ]

        h = mh.htmlTable(tabledata, widths)
        t_col = h.tcolour('black', '#d3d3d3')
        t_name = h.tname('Results')
        tables = h.assemble(t_name, t_col)

        page = mh.htmlPage('Race Results',
                        ['This Test Championship', 'This Test Race', '1981-01-01'],
                        [tables],
                        'powderblue')

        with open('page_test.html', 'w') as page_f:
            page_f.write(page.assemble())
        webbrowser.open('page_test.html')
    
    def test3_generate_seasoninfo(self):
        winners = self.dbobj.all_winners()
        s_info = self.dbobj.season_info()
        season_page =  mh.SeasonInfo('Season Info',
                                     [s_info['name'], s_info['year']],
                                     s_info,
                                     winners)
        season_page.create_page()
        

    def test4_generate_results(self):
        s_name = self.dbobj.season_info()['name']
        for event in self.db.events.find():
            e_name = event['event_name']
            res = self.dbobj.race_results(e_name)
            results_page = mh.RaceResults('Race Results',
                                            [e_name, 'Official Results'],
                                            res,
                                            s_name,
                                            e_name)

            results_page.create_page()

        
    def test5_generate_standings(self):
        standings = self.dbobj.chship_standings()
        season_name = self.dbobj.season_info()['name']

        standings_page = mh.StandingsPage('Standings',
                                          ['Official Standings', ''],
                                          standings,
                                          season_name)
        standings_page.create_page()


    def test6_generate_driver_pages(self):

        dr_stats = self.dbobj.all_drivers_history()
        for dr in list(dr['name'] for dr in list(self.db.drivers.find())):
            driver_page = mh.DriverStats('Driver Info',
                                         [dr, ''],
                                         dr,
                                         dr_stats[dr])
            driver_page.create_page()

if __name__ == '__main__':
    unittest.main()

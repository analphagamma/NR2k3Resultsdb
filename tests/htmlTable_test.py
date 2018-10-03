import unittest
from pprint import pprint
import webbrowser
from context import make_html as mh
from context import make_html_v as mh_v
from context import dbhandler
from pymongo import MongoClient

class TableTest(unittest.TestCase):

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
    
    @unittest.skip('')
    def test3_generate_results(self):
        dbobj = dbhandler.DBHandler('Unipart Series.ini')
        winners = dbobj.all_winners()
        season_page =  mh.SeasonInfo(dbobj.season_info(), winners)
        season_page.build_page()        
       
    def test4_generate_results(self):
        dbobj = dbhandler.DBHandler('Unipart Series.ini')
        res = dbobj.race_results('The Grapevine 175')
        s_name = dbobj.season_info()['name']
        e_name = 'The Grapevine 175'
        results_page = mh_v.RaceResults('Race Results',
                                        [e_name, 'Official Results'],
                                        res,
                                        s_name,
                                        e_name)

        results_page.build_page()
        
    @unittest.skip('')
    def test5_generate_standings(self):
        dbobj = dbhandler.DBHandler('Unipart Series.ini')
        standings = dbobj.chship_standings()
        season_name = dbobj.season_info()['name']

        standings_page = mh_v.StandingsPage('Standings',
                                            ['Official Standings', ''],
                                            standings,
                                            season_name)
        standings_page.build_page()

    @unittest.skip('')
    def test6_generate_driver_pages(self):
        client = MongoClient('mongodb://localhost:27017/')
        client.server_info()
        db = client.chship
        dbobj = dbhandler.DBHandler('Unipart Series.ini')
        dr_stats = dbobj.all_drivers_history()
        for dr in db.drivers.find():
            driver_page = mh.DriverStats(dr['name'], dr_stats[dr['name']])
            driver_page.build_page()

if __name__ == '__main__':
    unittest.main()

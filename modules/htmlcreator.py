class htmlTable:
    ''' Creates a table in html.

        In:
            table_list -> list of lists. Every element is a ro
                in the table. The inner list contains the column values.
            col_widths -> list of integers. The length should be the same
                as the number of columns.

        Out:
            It outputs the html for the table.

        Usage:
            Instantiate the object
            self.tformat() -> Enter the colour of the border and the table background
            self.tname() -> The name of the table
            '''
            
    def __init__(self, table_data: list, col_widths: list):
        self.table_data = table_data
        self.col_widths = col_widths
        self.rows = []

    def tcolour(self, borderc: str, backgroundc: str):
        ''' Sets the colour of the table border and the colour of the background '''
        
        return '<table style="width: {}px; border-color: {}; background-color: {}; margin-left: auto; margin-right: auto;" border="black">\n'.format(sum(self.col_widths), borderc, backgroundc)

    def tname(self, table_name: str):
        ''' Sets the name of the table and puts it in the centre. '''
        
        return '<p style="text-align: center;"><span style="text-decoration: underline;"><strong>{}</strong></span></p>\n'.format(table_name)

    def add_column(self, width: int, text: str, header=False):
        ''' Adds a single column. Makes it bold if it's the table header. '''
        
        bold_tags = ('<em><strong>', '</strong></em>') if header else ('','')
        return '<td style="width: {}px; text-align: center;">{}{}{}</td>\n'.format(width, bold_tags[0] ,text, bold_tags[1])

    def insert_row(self, row):
        ''' Makes a whole row from the list of column values.'''
        
        isHeader = True if self.rows == ['<tr>\n'] else False
        
        self.rows.append(''.join([self.add_column(self.col_widths[w], v, header=isHeader) for w, v in enumerate(row)]))

    def assemble_table(self, name, colours):
        ''' Puts together all the elements of the table and returns it as a string. '''
        
        for row in self.table_data:
            self.rows.append('<tr>\n')
            self.insert_row(row)
            self.rows.append('\n</tr>\n')
        return name + colours + '<tbody>\n' + ''.join(self.rows) + '</tbody>\n' + '</table>'
        
class htmlPage:
    ''' The parent class of all the different page formats.
        It is instantiated with a
             - head -> head text
             optional:
             - title_text -> a list of 2 strings [<h1>, <h2>] used as titles
             - bg_colour -> name or hex of a colour if you don't like powderblue '''
             
    
    
    def __init__(self, head: str, title_text: list, bg_colour='powderblue'):
        self.head = head
        self.title_text = title_text
        self.bg_colour = bg_colour

        # these are overridden in the subclasses.
        self.filename = '_'
        self.widths = []
        self.tabledata = [[]]

    def make_href(self, from_str: str, to_str: str):
        ''' Transforms a string into a href.
            //Not implemented yet.// '''
            
        return '<a href="{}">{}</a>'.format(to_str, from_str)

    def build_tables(self):
        ''' Puts together the tables from the tabledata list of lists and the widths of all the columns and
            gives it a name and a colour. '''
            
        t = htmlTable(self.tabledata, self.widths)
        t_col = t.tcolour('black', '#d3d3d3')
        t_name = t.tname('_')
        table = t.assemble_table(t_name, t_col)
        return table
        

    def assemble(self):
        ''' Returns the whole page's html code in a single string.'''
        
        opening_tags = '<html>\n<body style="background-color:{};">\n<head><title>\n'.format(self.bg_colour)
        title1 = '<h1 style="text-align: center;">{}</h1>\n'.format(self.title_text[0])
        title2 = '<h2 style="text-align: center;">{}</h2>\n'.format(self.title_text[1])
        body_tags = '</title></head>\n<body>\n'
        tables = ''.join(self.build_tables())
        closing_tags = '</body>\n</html>'
        return opening_tags + self.head + body_tags + title1 + title2  + tables + closing_tags

    def create_page(self):
        ''' Saves the html file with the correct filename into the
            tables sub-directory.'''
            
        with open('./tables/'+self.filename+'.html', 'w') as page_f:
            page_f.write(self.assemble())

class DriverStats(htmlPage):
    ''' Webpage for an individual driver's results and statistics.
        On top of the attributes of teh parent class you have to provide:
            - driver_name -> <(first name initial) (surname)'(nickname)'>
            - driver_stats -> list from dbhandler.DBHandler.all_drivers_history()

        Usually this page is created in bulk for all the drivers at once. '''
        
    

    def __init__(self, head: str, title_text: str, driver_name: str, driver_stats: list):
        super().__init__(head, title_text)
        self.driver_name = driver_name
        self.driver_stats = driver_stats
        self.filename = 'driver_'+ \
                        self.driver_name.replace(' ', '_') \
                                        .replace('\'', '')
        self.widths = [18, 300, 300, 18, 18, 18, 45, 80]
        self.tabledata = [['No.',
                          'Event',
                          'Track',
                          'Finish',
                          'Start',
                          'Laps Led',
                          'Most Led',
                          'Status']]
                
        for event in self.driver_stats:
            event[1] = self.make_href(event[1],
                                'race_' + event[1].replace('\'', '').replace(' ', '_') + '.html')
            event[2] = self.make_href(event[2],
                                'track_' + event[2].replace('\'', '').replace(' ', '_') + '.html')
            self.tabledata.append(event)

    '''TBA: add driver statistics? '''

class StandingsPage(htmlPage):
    ''' A webpage that shows the current standings in the championship.
        Column widths and table headers are predetermined.
        On top of the parent classes attribute you have to provide:
            - standings -> a list of lists from dbhandler.DBHandler.chship_standings()
            - season_name -> a string entered either manually or from dbhandler.DBHandler.season_info()'''
                  
    def __init__(self, head: str, title_text: list, standings: list, season_info: str):
        super().__init__(head, title_text)
        self.standings = standings
        self.season_info = season_info
        self.filename = 'standings_'+ \
                        self.season_info['year'] + \
                        '_' + \
                        self.season_info['name'].replace(' ', '_') \
                                                .replace('\'', '') \
                                                .replace('(', '_') \
                                                .replace(')', '_')

        season_file_name = 'season_'+ \
                           self.season_info['year'] + \
                           '_' + \
                           self.season_info['name'].replace(' ', '_') \
                                                   .replace('\'', '') \
                                                   .replace('(', '_') \
                                                   .replace(')', '_') + \
                           '.html'
        title_text[1] = self.make_href('Season Info', season_file_name)
                    
        self.widths = [18,250,100,18,18,18,18,50,50,18,18,18]
        self.tabledata = [['P',
                          'Driver',
                          'Points',
                          'Wins',
                          'Top5s',
                          'Top10s',
                          'Poles',
                          'Avg Finish',
                          'Avg Start',
                          'Laps Led',
                          'DNFs',
                          'Starts']]

        for i, row in enumerate(self.standings):
            row[0] = self.make_href(row[0],
                                    'driver_' + row[0].replace('\'', '').replace(' ', '_') + '.html')
            self.tabledata.append([i+1, *row])

class RaceResults(htmlPage):
    ''' The html format of a race results of a given season.
        On top of the attributes of the parent class you have to provide:
            - results -> a list of dictionaries from dbhandler.DBHandler.race_results()
            - season_name }
            - event_name  } -> both entered either manually or from dbhandler.DBHandler.season_info()'''
                   
    def __init__(self, head, title_text, results: list, season_name: str, event_name):
        super().__init__(head, title_text)
        self.results = results
        self.season_name = season_name
        self.event_name = event_name
        self.filename = 'race_'+ \
                        event_name.replace(' ', '_') \
                                  .replace('\'', '') \
                                  .replace('(', '_') \
                                  .replace(')', '_')
        self.widths = [18,18,65,18,180,65,45,45,60,50,50]
        self.tabledata = [['P',
                           'S',
                           'Q Time',
                           '#',
                           'Driver',
                           'Interval',
                           'Laps',
                           'Led',
                           'Led Most',
                           'Points',
                           'Status']]

        for row in self.results:
            row['driver'] = self.make_href(row['driver'],
                                           'driver_' + row['driver'].replace('\'', '').replace(' ', '_') + '.html')
            self.tabledata.append([row['r_position'],
                                  row['q_position'],
                                  row['q_time'],
                                  row['#'],
                                  row['driver'],
                                  row['interval'],
                                  row['laps'],
                                  row['laps_led'],
                                  row['most_led'],
                                  row['points'],
                                  row['status']
                                  ])
    
class SeasonInfo(htmlPage):
    ''' Webpage for the current season's data.
        On top of the attributes of teh parent class you have to provide:
            - season_info -> from dbhandler.DBHandler.season_info()
            - winners -> from dbhandler.DBHandler.all_winners() '''
                
    def __init__(self, head, title_text, season_info: dict, winners: dict):
        super().__init__(head, title_text)
        self.season_info = season_info
        self.winners = winners
        self.filename = 'season_'+ \
                        self.season_info['year']+ \
                        '_'+ \
                        self.season_info['name'].replace(' ', '_') \
                                                .replace('\'', '') \
                                                .replace('(', '_') \
                                                .replace(')', '_')
        self.widths = [120, 160, 100, 45, 160]
        self.tabledata = [['Date',
                          'Event Name',
                          'Track',
                          'Laps',
                          'Winner']]

        standings_file_name = 'standings_'+ \
                              self.season_info['year'] + \
                              '_' + \
                              self.season_info['name'].replace(' ', '_') \
                                                   .replace('\'', '') \
                                                   .replace('(', '_') \
                                                   .replace(')', '_') + \
                           '.html'
        title_text[1] = self.make_href('Standings', standings_file_name)

        for row in self.season_info['event_list']:
            event = row['event_name']
            event = self.make_href(event,
                                'race_' + event.replace('\'', '').replace(' ', '_') + '.html')
            track = self.winners[row['event_name']]['track']
            track = self.make_href(track,
                                'track_' + track.replace('\'', '').replace(' ', '_') + '.html')
            winner = self.winners[row['event_name']]['winner']
            winner = self.make_href(winner,
                                  'driver_' + winner.replace('\'', '').replace(' ', '_') + '.html')
            self.tabledata.append([row['date'],
                              event,
                              track,
                              row['no_of_laps'],
                              winner
                              ])

class TrackPage(htmlPage):

    def __init__(self, head, title_text, track_name: str, events: list):
        super().__init__(head, title_text)
        self.track_name = track_name
        self.events = events
        self.filename = 'track_' + \
                        self.track_name.replace(' ', '_') \
                                       .replace('\'', '')
        self.widths = [45, 160, 160]
        self.tabledata = [['No.',
                          'Event Name',
                          'Winner']]

        for ev in self.events:
            ev[1] = self.make_href(ev[1],
                                'race_' + ev[1].replace('\'', '').replace(' ', '_') + '.html')

            ev[2] = self.make_href(ev[2],
                                  'driver_' + ev[2].replace('\'', '').replace(' ', '_') + '.html')
            self.tabledata.append(ev)

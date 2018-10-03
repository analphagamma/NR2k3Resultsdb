import webbrowser

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

    def assemble(self, name, colours):
        ''' Puts together all the elements of the table and returns it as a string. '''
        
        for row in self.table_data:
            self.rows.append('<tr>\n')
            self.insert_row(row)
            self.rows.append('\n</tr>\n')
        return name + colours + '<tbody>\n' + ''.join(self.rows) + '</tbody>\n' + '</table>'
        
class htmlPage:

    def __init__(self, head: str, title_text: list, table_list: list, bg_colour: str):
        self.head = head
        self.title_text = title_text
        self.table_list = table_list
        self.bg_colour = bg_colour

    def make_href(self, chfrom: str):
        chto = chfrom.replace('\'', '').replace(' ', _) + '.html'
        return '<a href="{}">{}</a>'.format(chto, chfrom)

    def assemble(self):
        opening_tags = '<html>\n<body style="background-color:{};">\n<head><title>\n'.format(self.bg_colour)
        title1 = '<h1 style="text-align: center;">{}</h1>\n'.format(self.title_text[0])
        title2 = '<h2 style="text-align: center;">{}</h2>\n'.format(self.title_text[1])
        body_tags = '</title></head>\n<body>\n'
        tables = ''.join(self.table_list)
        closing_tags = '</body>\n</html>'
        return opening_tags + self.head + body_tags + title1 + title2  + tables + closing_tags
    
class StandingsPage:

    def __init__(self, standings: list, season_name: str):
        self.standings = standings
        self.season_name = season_name

    def build_page(self):
        
        widths = [18,180,100,18,18,18,18,50,50,18,18,18]
        tabledata = [['P',
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
            tabledata.append([i+1, *row])

        t = htmlTable(tabledata, widths)
        t_col = t.tcolour('black', '#d3d3d3')
        t_name = t.tname('Standings')
        table = t.assemble(t_name, t_col)
        page = htmlPage('Championship Standings',
                        [self.season_name, ''],
                        [table],
                        'powderblue')

        with open('standings.html', 'w') as page_f:
            page_f.write(page.assemble())
        #webbrowser.open('standings.html')

class RaceResults:
    ''' The html format of a race results of a given season. '''
    
    def __init__(self, results: dict, season_name: str, event_name):
        self.results = results
        self.season_name = season_name
        self.event_name = event_name

    def build_page(self):
        ''' Builds the webpage, saves the file and opens it. '''

        widths = [18,18,65,18,180,65,45,45,60,50,50]
        tabledata = [['P',
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
            tabledata.append([row['r_position'],
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

        t = htmlTable(tabledata, widths)
        t_col = t.tcolour('black', '#d3d3d3')
        t_name = t.tname('Results')
        table = t.assemble(t_name, t_col)
        page = htmlPage('Race Results',
                        [self.season_name, self.event_name],
                        [table],
                        'powderblue')

        with open('race.html', 'w') as page_f:
            page_f.write(page.assemble())
        #webbrowser.open('race.html')
        
class DriverStats:

    def __init__(self, driver_name: str, driver_stats: list):
        self.driver_name = driver_name
        self.driver_stats = driver_stats

    def build_page(self):
        
        widths = [18, 300, 300, 18, 18, 18, 45, 80]
        tabledata = [['No.',
                      'Event',
                      'Track',
                      'Finish',
                      'Start',
                      'Laps Led',
                      'Most Led',
                      'Status']]

        
        for event in self.driver_stats:
            tabledata.append(event)

        t = htmlTable(tabledata, widths)
        t_col = t.tcolour('black', '#d3d3d3')
        t_name = t.tname('Driver Info')
        table = t.assemble(t_name, t_col)
        page = htmlPage(self.driver_name,
                        ['', ''],
                        [table],
                        'powderblue')

        filename = self.driver_name.replace(' ', '_').replace('\'', '')
        with open(filename+'.html', 'w') as page_f:
            page_f.write(page.assemble())
    
class SeasonInfo:
    ''' The html format of the current season's data. '''
    
    def __init__(self, season_info: dict, winners: dict):
        self.season_info = season_info
        self.winners = winners

    def build_page(self):
        ''' Builds the webpage, saves the file and opens it. '''
        
        widths = [160, 160, 100, 45, 160]
        tabledata = [['Date',
                      'Event Name',
                      'Track',
                      'Laps',
                      'Winner']]

        for row in self.season_info['event_list']:
            print(row['event_name'])
            tabledata.append([row['date'],
                              row['event_name'],
                              self.winners[row['event_name']]['track'],
                              row['no_of_laps'],
                              self.winners[row['event_name']]['winner']
                              ])

        t = htmlTable(tabledata, widths)
        t_col = t.tcolour('black', '#d3d3d3')
        t_name = t.tname('Season')
        table = t.assemble(t_name, t_col)
        page = htmlPage('Season Schedule',
                        [self.season_info['name'], self.season_info['year']],
                        [table],
                        'powderblue')

        with open('season.html', 'w') as page_f:
            page_f.write(page.assemble())
        #webbrowser.open('season.html')

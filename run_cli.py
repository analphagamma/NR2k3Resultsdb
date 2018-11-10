import os, sys
from tableoutput import TableOutput
from modules.dbhandler import DBHandler

class Menu():
    '''This is the class for all menu-related methods.
       It displays menus, handles all user-input and calls database commands from the other class.'''
    

    def show_menu(self, menu_name, options):
        '''Displays any menus and executes the requested functions
        [In]:
            menu_name -> str - The name of the menu in the head
            options -> dict - available options in the menu
                              key: str - The character by which the option can be called
                              value: list - value[0] - func - the function to execute
                                            value[1] - str - option text
                                            value[2] - str - prompt text
                                    
        [Out]:
            boolean - None: exits the application
                      True: clears the screen and displays the menu again
                                (in case of incorrect input or aborted authentication)'''
       
        while True:
            #displays available options in the menu
            os.system('clear')
            print(menu_name)
            print('=' * len(menu_name) + '\n')
            
            for num, option in sorted(options.items()):
                print(num, ' - ', option[1])
                        
            q = input('\nPlease select an option from above or enter \'quit\' to exit\n>').lower().strip(' ')
            if q == 'quit': 
                print('\nExiting.')
                return None
            if q not in options.keys():
                return True
            else:
                #execute requested function
                while True:
                    os.system('clear')
                    print(options[q][1])
                    print('=' * len(options[q][1]))
                    print(options[q][2])
                    if not options[q][0]():
                        input('\nPress enter to continue.')
                        break

class MenuActions():

    def create_new(self):
        ''' Creates a new season. '''
        confirm = False
        while not confirm:
            confirm = input('Enter "quit" to go back to the main menu\n>')
        if confirm == 'quit':
            return None
        elif confirm != dbobj.series_ini:
            print('Ini file does not match.')
        else:
            dbobj.create_database()
            confirm = True
            return None
    
    def reset_database(self):
        ''' Query and confirmation to clear all collections from the db. '''

        confirm = False
        while not confirm:
            confirm = input('Are you sure? (y/n)\n>')
            if confirm not in ['y', 'n']:
                print('Please enter y or n.')
                confirm = False
            elif confirm == 'n':
                return None
            elif confirm == 'y':
                dbobj.reset_db()
                confirm = True
        return None

    def enter_results(self):
        ''' Query of folder name where results are found. '''
        
        results_entered = False
        while not results_entered:
            results_dir = input('\nPlease enter the subfolder\'s name where you saved the results or enter "quit".\n(eg. "whatever" will mean exports_imports\\whatever)\n> ')
            if os.path.isdir('./exports_imports/'+results_dir):
                results_entered = True
            elif results_dir == 'quit':
                return None
            else:
                print('Folder not found.')

        point_sys_input = input('\nPlease enter the name of the point system you wish to use\n>')
        setattr(dbobj, 'point_system', point_sys_input)

        dbobj.enter_season_result(results_dir)

        print("Results entered.")

        t_obj = TableOutput(series)
        t_obj.generate_output()
        sys.exit(0)

    def generate_pages(self):
        ''' Remakes all the webpages without having to go through the database inserts. '''
        t_obj = TableOutput(series)
        t_obj.generate_output()
        sys.exit(0)

    def menu_options(self):
        return {'1': [self.create_new, 'Create New Season', 'Please re-enter your series ini.\nCaution! This will re-write an existing season'],
                '2': [self.reset_database, 'Reset Database', 'This option will delete all data from this series'],
                '3': [self.enter_results, 'Enter Results & Generate HTML tables', ''],
                '4': [self.generate_pages, 'Generate webpages', '']}


if __name__ == '__main__':
    db_open = False
    while not db_open:
        series = input('\nPlease enter series ini file name\n(eg. Whatever Cup.ini)\n> ')
        try:
            dbobj = DBHandler(series)
        except FileNotFoundError:
            print('This ini file doesn\'t seem to exist.')
        else:
            db_open = True
            
    menu = Menu()
    actions = MenuActions()
    while True:
        if not menu.show_menu('nrk3 Results Database', actions.menu_options()):
            break

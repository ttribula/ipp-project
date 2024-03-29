import getopt
import sys


class ArgCheck:
    def __init__(self):
        self.source = ''
        self.input = ''

    def get_source(self):
        return self.source

    def get_input(self):
        return self.input

    def check(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], '', ['help', 'input=', 'source='])
        except getopt.GetoptError as err:
            exit(10)
        if len(opts) > 2:
            exit(10)
        is_input = is_source = 0
        for opt, val in opts:
            if opt == '--help':
                # TODO: HELP PRINT
                print('help')
                if len(opts) != 1:
                    exit(10)
                exit(0)
            elif opt == '--input' and not is_input:
                is_input = 1
                self.input = val
            elif opt == '--source' and not is_source:
                is_source = 1
                self.source = val
            else:
                exit(10)

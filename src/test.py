import logging, re, datetime, sys, traceback


from romdb import tvparser
from romdb.romlog import *

def non_destructive_test():

    scanner = tvparser.TVParser('/home/steini/tvtesttree')
    try:
        scanner.scan_source()
    except:
        pass

    test_log.info(
        '\n--------------------------\n%s - Start of new test.\n------------------\n' % datetime.datetime.now()
        )
    test_log.info('\nPROPER EPS\n\n')
    [test_log.info('%s\n'%ep) for ep in scanner.parsed_eps]
    test_log.info( '\n\nUNPARSABLE EPS\n')
    [test_log.info('%s\n'%ep) for ep in scanner.unparseable_eps]
    test_log.info('\n\nSINGLE EP DIRS\n')
    [test_log.info('%s\n'%ep) for ep in scanner.single_ep_dirs]

    test_log.info('Number of parsed_eps = %d' % len(scanner.parsed_eps))
    test_log.info('Number of unparseable_eps = %d' % len(scanner.unparseable_eps))
    test_log.info('Number of single_ep_dirs = %d' % len(scanner.single_ep_dirs))


def regex_test():
    testcases = [
        'series name season 1',
        'series.name.s01e02.some.shit',
        'episode 1',
        'season 1 episode 2',
        'season 2',
        'series name season 1 episode 2'
        ]
    for case in testcases:
        match = None
        for regex in tv_regexes:
            match = re.match(regex.pattern, case)
            if match: break
        if match:
            test_log.info('SUCCESS: case [%s] matched pattern [%s]' % (case, regex.pattern))
        else:
            test_log.info('FAILURE: case [%s] did not match anything' % (case))


def my_excepthook(etype, value, tback):
    print 'this is the cool excepthook'
    #sys.__excepthook__(etype, value, tback)
    s = ''.join(traceback.format_exception(etype, value, tback))
    print 'UNEFINED EXCEPTION OCCURED:\n\n%s\n' % (s,)

if __name__ == "__main__":
    sys.excepthook = my_excepthook
    rom_log.setLevel(logging.DEBUG)
    test_log.setLevel(logging.DEBUG)
    non_destructive_test()

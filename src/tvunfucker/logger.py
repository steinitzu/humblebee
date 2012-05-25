import logging

#romlog
log = logging.getLogger('tvunfucker')
formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s.%(funcName)s: %(message)s')
streamhdlr = logging.StreamHandler()
streamhdlr.setFormatter(formatter)

file_handler = logging.FileHandler('romlog.log',  mode='a')
file_handler.setFormatter(logging.Formatter('%(levelname)s %(asctime)s %(module)s.%(funcName)s: %(message)s'))

log.addHandler(file_handler)
log.addHandler(streamhdlr)


#testlog
test_log = logging.getLogger('testlog')
file_handler = logging.FileHandler('testlog.log',  mode='a')
file_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
test_log.addHandler(file_handler)
test_log.setLevel(logging.DEBUG)

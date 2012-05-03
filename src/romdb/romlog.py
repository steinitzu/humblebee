import logging

rom_log = logging.getLogger('romdb')
formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s.%(funcName)s: %(message)s')
streamhdlr = logging.StreamHandler()
streamhdlr.setFormatter(formatter)
rom_log.addHandler(streamhdlr)


test_log = logging.getLogger('testlog')
file_handler = logging.FileHandler('testlog.log',  mode='a')
file_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
test_log.addHandler(file_handler)
test_log.setLevel(logging.DEBUG)


def log_info(text):
    rom_log.info(text)
    

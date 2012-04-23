import logging

rom_log = logging.getLogger('romdb')
formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s.%(funcName)s: %(message)s')
streamhdlr = logging.StreamHandler()
streamhdlr.setFormatter(formatter)
rom_log.addHandler(streamhdlr)



def log_info(text):
    rom_log.info(text)
    

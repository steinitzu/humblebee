"""
This module will initialize the config parsers.\n
There are two parsers.\n
One for the default config file and one for the user config.\n
\n
If a user config file does not exist, it will be created here on import.\n
Use the |get| and |set| methods to retrieve and set config values.\n
|get| will always prefer user config over default config when possible.\n
|read| will re-read the user config file and |write| will write any changes you have
made back to the file.
"""
import ConfigParser, sys, os, logging

import util


rtlog = logging.getLogger('runtundi')
#from . import __init__ as runtundi

def get_user_config():
    """
    Finds the user config file in a platform specific way.\n
    Returns the config file's path regardless of
    wheather it exists or not.  
    """
    config_path = None
    if sys.platform == 'win32':
        config_path = os.path.join(
            os.environ['APPDATA'],
            util.program_name,
            util.program_name+'.cfg'
            )
    else:
        #use ~/.program_name
        config_path = os.path.join(
            os.path.expanduser('~'),
            '.'+util.program_name,
            util.program_name+'.cfg'
            )
    return config_path


default_config = ConfigParser.RawConfigParser()
default_config_path = os.path.join(os.path.dirname(__file__), 'default.cfg')
#find the default config file
default_config.read(default_config_path)

cfg_path = get_user_config()
user_config = ConfigParser.RawConfigParser()

#Make the file
if not os.path.exists(cfg_path):
    try:
        os.makedirs(os.path.dirname(cfg_path))
    except OSError as e:
        if e.errno == 17:
            pass
        else:
            raise        
    f = open(cfg_path, 'w')
    f.close()
    

def set(section, option, value):
    """
    set(section, option, value)\n
    This method sets an option in user_config.\n
    IT does not write the config file.
    This is so many options can be edited faster and
    reverted if needed.\n
    They will all be written at once with write_config.
    """
    user_config.read(cfg_path)
    if not user_config.has_section(section):
        user_config.add_section(section)
    user_config.set(section, option, value)


def get(section, option, as_type=None):
    """
    get(section, option, as_type=None)\n
    get(str, str, as_type=type)\n

    as_type accepts bool, float and int\n
    will return a string if it's None or assume the type
    or whatever it is that ConfigParser does.
    """
    tmap = {
        int : user_config.getint,
        float : user_config.getfloat,
        bool : user_config.getboolean,
        None : user_config.get
        }
    dtmap = {
        int : default_config.getint,
        float : default_config.getfloat,
        bool : default_config.getboolean,
        None : default_config.get
        }        
    result = None
    try:
        result = tmap[as_type](section, option)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
        #error will be raised if this fails since that means
        #caller passed an invalid option/section
        result = dtmap[as_type](section,option)
    return result

def write_user_config():
    """
    This will write the current state of user_config
    to the config file.
    """
    with open(cfg_path, 'wb') as cfgfile:
        user_config.write(cfgfile)
    read_user_config()

def read_config():
    """
    Updates the user_config object from file.
    """
    user_config.read(cfg_path)    
    default_config.read(default_config_path)

read_config()

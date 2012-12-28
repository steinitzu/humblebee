import sys, os
from ConfigParser import NoOptionError, NoSectionError, RawConfigParser

from .texceptions import InvalidArgumentError
from .util import safe_make_dirs, str_to_bool

class ThreeTierConfigParser(RawConfigParser):
    """
    Config parser with 3 configs
    1. global config (stored in default_cfg_path)
    2. user config (stored in user_cfg_path)
    3. runtime config (stored in memory)

    option foo, section bar from user config will always override the 
    same option in global config if available.
    Options in runtime config will override user config in the same way.
    """

    def __init__(self, program_name, global_config_path=None, runtime_options={}, *a, **kw):
        """
        See |import_to_runtime_parser| method for format of runtime options.
        """
        self.program_name = program_name
        RawConfigParser.__init__(self, *a, **kw)
        self.user_cfg_path = self._get_user_cfg_path()        
        try:
            if os.path.exists(global_config_path):
                self.global_cfg_path = global_config_path
            else:
                self.global_cfg_path = None
        except TypeError:
            self.global_cfg_path = None

        self.user_parser = RawConfigParser()        
        self.global_parser = RawConfigParser() if self.global_cfg_path else None
        self.runtime_parser = RawConfigParser()                
        self.__runtime_options = runtime_options
        self.initialize()

    def initialize(self):
        try:
            open(self.user_cfg_path)
        except IOError as e:
            if e.errno == 2:
                self._create_user_cfg_file()
        self.read_all()
        self.import_to_runtime_parser(self.__runtime_options)

    def _create_user_cfg_file(self):
        if os.path.exists(self.user_cfg_path):
            return
        safe_make_dirs(
            os.path.split(self.user_cfg_path)[0]
            )                
        try:
            f = open(self.user_cfg_path, 'w')
        finally:
            f.close()

    def _get_user_cfg_path(self):
        """
        Get path to user config regardless of whether it exists or not.
        On Windows, path is "%APPDATA%/program_name/program_name.cfg"
        On *nix it is '~/.program_name/program_name.cfg'
        This function does not create any files.
        """
        if sys.platform == 'win32':
            #%APPDATA%/program_name/program_name.cfg
            config_path = os.path.join(
                os.environ['APPDATA'],
                self.program_name,
                self.program_name+'.cfg'
                )
        else:
            #~/.program_name/program_name.cfg
            config_path = os.path.join(
                os.path.expanduser('~'),
                '.'+self.program_name,
                self.program_name+'.cfg'
                )            
        return config_path

    @classmethod
    def get_global_cfg_path(self, program_name):
        """        
        Get the default path to global config. 
        Just a convenience function, never used internally.
        Windows: '%ALLUSERSPROFILE%/program_name/program_name.cfg'
        *nix: '/etc/program_name/program_name.cfg'
        """
        if sys.platform == 'win32':
            cfg_path = os.path.join(
                os.environ['ALLUSERSPROFILE'],
                program_name,
                program_name+'.cfg'
                )
        else:
            cfg_path = os.path.join(
                '/etc',
                program_name,
                program_name+'.cfg'
                )
        return cfg_path


    def get(self, section, option, as_type=None):
        """
        get(section, option, as_type=None) -> object
        Try to get the given section and option from one of the parser.
        Starts with runtime_parser, falls back on user_parser which falls back on 
        global_parser.
        If all parsers fail, a NoOptionError or NoSectionError will be raised.

        Return value will be cast to |as_type| type if not None.
        If as type is None, a string is returned.
        Guaranteed supported types as int, float and bool
        """
        excp = (NoOptionError, NoSectionError)
        try:
            result = self.runtime_parser.get(section, option)
        except excp as e:
            try:
                result = self.user_parser.get(section, option)
            except excp as e:
                if not self.global_parser:
                    raise
                else:
                    result = self.global_parser.get(section, option)
        if as_type:
            if as_type==bool:
                return str_to_bool(result)
            else:
                return as_type(result)                
        return result

    def set(self, section, option, value, parser='user', write=False):
        """
        set(section, option, parser='user', write=False)        
        Set given option in given section to given value.
        Section is implicitly created if it does not exist.
        The |parser| argument can be either 'user' or 'runtime'.
        If write==True the config file (if any) will also be written 
        with the new value.
        """
        if parser=='user': p = self.user_parser
        elif parser=='runtime': p = self.runtime_parser
        else: 
            raise InvalidArgumentError(
                '"%s" is not a valid argument for parser' % parser
                )
        if not p.has_section(section):
            p.add_section(section)
        p.set(section, option, value)
        if write and parser == 'user':
            p.write(self.user_cfg_path)
        

    def read_all(self):
        """
        Read settings from user and global config files.
        """
        self.user_parser.read(self.user_cfg_path)
        if self.global_parser:
            self.global_parser.read(self.global_cfg_path)

    def write_user_config(self):
        """
        Write settings from user_parser to file user_cfg_path.
        """  
        f = None
        try:
            f = open(self.user_cfg_path, 'w')
            self.user_parser.write(f)
        finally:
            f.close()


    def import_to_runtime_parser(self, dicti):
        """
        import_to_runtime_parser(dict)
        Create sections and options/values from given dict and 
        set to runtime_parser.
        dict should be in format 
        {'section_name':{'option1':'value1', option2:'value2'}}
        """
        for section,v in dicti.iteritems():
            #self.runtime_parser.add_section(section)
            for option,value in v.iteritems():
                self.set(section, option, value, parser='runtime')
            
                
            

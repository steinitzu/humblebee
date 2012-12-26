import unittest, os

from tvunfucker import cfg

class Test_Cfg(unittest.TestCase):
    @classmethod
    def setUp(self):
        dfg = os.path.join(
            os.path.dirname(__file__),
            'tvunfucker/default.cfg'
            )
        self.cfgparser = cfg.ThreeTierConfigParser(
            'test_program_tvuf', 
            global_config_path=dfg
            )
        self.cfgparser.initialize()

    def tearDown(self):
        pass


    def test_set_get(self):
        self.cfgparser.set('newsection', 'dasoption', 45, parser='user')
        v = self.cfgparser.get('newsection', 'dasoption')
        self.assertEquals(v, 45)

    def test_set_write_read_get(self):
        self.cfgparser.set('newsection', 'dasoption', False, parser='user')
        self.cfgparser.write_user_config()
        self.cfgparser.read_all()
        v = self.cfgparser.get('newsection', 'dasoption', as_type=bool)
        self.assertEquals(v, False)

    def test_make_get_runtime_cfg(self):
        v = {'cake':{'flavor':'chocolate','candles':5,'is_lie':True}}
        self.cfgparser.import_to_runtime_parser(v)
        self.assertEquals(self.cfgparser.get('cake', 'is_lie'), True)

    def test_runtime_cfg_override(self):
        """Test if runtime cfg overrides user cfg properly."""
        v = self.cfgparser.get('cake', 'islie')
        self.assertEquals(v, 'yes')
        self.cfgparser.set('cake', 'islie', 'no', parser='runtime')
        v = self.cfgparser.get('cake', 'islie')
        self.assertEquals(v, 'no')
        

unittest.main()        

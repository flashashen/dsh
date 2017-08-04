from cmd_base import CmdBase


class CmdDb(CmdBase, object):

    def __init__(self):
            super(self.__class__, self).__init__()
            self.name = 'db'
            self.prompt = '(db)'
            self.add_default_command_delegation()
            self.engines = {}
            self.cfg = None


    def configure(self, cfg_obj=None):
        if not cfg_obj or not cfg_obj.cfg:
            return

        self.cfg =  cfg_obj.cfg
        if 'db' not in self.cfg:
            self.cfg['db'] = {}


    def do_get(self, line):

        try:
            segs = line.split()
            print str(self.get_engine(segs[0]))
        except Exception as e:
            print "failed to get engine for {}: {}".format(segs[0], e)


    def help_get(self):
        print 'This command returns a sqlalchemy engine object. \nUsage: get <cfg_name>'

    def complete_get(self, text, line, begidx, endidx):
        return [x for x in self.cfg['db'] if x.startswith(text)]



    def get_engine(self, cfg_name, db=None, echo=False):
        if cfg_name:
            if cfg_name in self.engines:
                # the engine is already setup. just return it
                return self.engines[cfg_name]
            elif cfg_name in self.cfg['db']:
                # setup the engine
                import sqlalchemy
                from sqlalchemy import text
                config = self.cfg['db'][cfg_name]
                url_format_string = "{:s}://{:s}:{:s}@{:s}:{:s}/{:s}?charset=utf8"

                print("creating db engine for " + url_format_string.format(
                    config['driver'],
                    config['user'],
                    'redacted',
                    config['host'],
                    str(config['port']),
                    db if db else config['name']))

                self.engines[cfg_name] = sqlalchemy.create_engine(url_format_string.format(
                    config['driver'],
                    config['user'],
                    config['pass'],
                    config['host'],
                    str(config['port']),
                    db if db else config['name']),
                    connect_args=config['args'],
                    echo=echo)
                return self.engines[cfg_name]
            else:
                print '{} is not a known engine config. Defined configurations are: {}'.format(cfg_name, self.cfg['db'].keys())

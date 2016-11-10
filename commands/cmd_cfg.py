import os, cmd, pprint
import subprocess
import yaml

import cmd_base
from cmd_base import CmdBase

class CmdConfig(CmdBase, object):


    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self, on_load=None):

        super(self.__class__, self).__init__()

        self.name = 'cfg'
        self.on_load = on_load
        self.cfg = {}
        self.cmd = {}
        self.add_default_command_delegation()

    #
    # def do_cfg(self, line):
    #     try:
    #         getattr(self, 'do_'+line)(line)
    #     except:
    #         print "no command '{}'".format(line)
    #
    #
    # def complete_cfg(self, text, line, begidx, endidx):
    #     return self.generic_class_based_complete(text, line, begidx, endidx)
    #      # return [c for c in self.completenames(text, line, 0, 0) if 'do_'+c not in dir(CmdBase)]
    #     # return self.completeFromNestedDict(line, self.cmd_tree)


    def help_cfg(self):
        print("\ncfg help here\n")




    def get_cfg(self, name=None):
        if name:
            return self.cfg[name] if name in self.cfg else None
        else:
            return self.cfg



    def do_list(self, line):

        print("\n")
        for cname in self.cfg:
            print(cname + ':\n')
            self.pp.pprint(self.cfg[cname])
            print("\n")

        print("\ncommand tree:")
        self.pp.pprint(self.cmd)


    def do_load(self, line):
        self.configure()
        # call the handler for the config loaded 'event'


    def do_search(self, line):
        import fnmatch
        matches = []
        for root, dirnames, filenames in os.walk(os.path.expanduser('~')):
            for filename in fnmatch.filter(filenames, '.cmd.yml'):
                matches.append(os.path.join(root, filename))
        print(matches)

    def do_edit(self, line):
        from subprocess import call
        EDITOR = os.environ.get('EDITOR','vim') #that easy!
        call([EDITOR, os.path.expanduser('~/.cmd.yml')])
        self.configure()


    #
    # def help_venv(self):
    #     print "usage: venv init|activate"
    # def do_venv(self, line):
    #
    #     segments = line.split()
    #     if len(segments) < 2:
    #         self.do_help()
    #
    #     sub_cmd = segments[1]
    #     # if sub_cmd == 'install':
    #     #     print sub_cmd + 'not implemeted'
    #     #     return
    #
    #     if sub_cmd == 'init':
    #         self.execute('virtualenv .env', '')
    #         return
    #
    #     if sub_cmd == 'activate':
    #         self.execute('source .env/bin/activate', '  ')
    #         return



        # Configure. The first time this is called the master_cfg will be None and the whole
    # system gets configured in on_load. This method will be called again during the on_load
    # but at that point master_cfg will be set and nothing will be done.
    def configure(self, cfg_obj=None):

        if not cfg_obj:
            with open(os.path.expanduser('~') + '/.cmd.yml') as cfgfile:
                self.cfg = cmd_base.cfg_expanduser(yaml.load(cfgfile.read()))
            if self.on_load:
                self.on_load(self)




if __name__ == '__main__':

    cmdcfg = CmdConfig();
    cmdcfg.configure()
    cmdcfg.cmdloop_ignore_interrupt()


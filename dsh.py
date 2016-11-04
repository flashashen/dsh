import cmd
import os
import pprint
import subprocess
import sys
import traceback

import yaml

from commands.cmd_base import CmdBase
from commands.cmd_prj import CmdProject
from commands.cmd_cfg import CmdConfig
from commands.cmd_docker import CmdDocker



class CmdDSH(CmdBase, object):


    def __init__(self):


        # self.cmd_tree = {'cfg':
        #                      {'list':'',
        #                       'load':'',
        #                       'search: '','
        #                       'edit':''}}


        # Create config object.
        def on_load(loaded_config):
            self.configure(loaded_config)
        self.cfg = CmdConfig(on_load)

        self.imported_cmds = [CmdProject(), CmdDocker(), self.cfg]

        # Let the config object setup everything
        self.cfg.configure()




        super(self.__class__, self).__init__()



    def configure(self, master_cfg=None):

        # Initialize imported commands and create do, complete, and help methods for
        # each command, delegating to the command object
        for cmd_obj in self.imported_cmds:
            cmd_obj.configure(self.cfg.get_cfg())
            self.load_commands_class(cmd_obj)


    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext) and not a in ['do_EOF','do_shell'] ]


    def load_commands_class(self, cmd_obj):
        """
        Setup do, help, complete methods from submodule to main. Also do any other
        dynamic class setup necessary.

        :param cmd_obj:  The subcommand module object.
        :return: None
        """
        # for cmd_obj in self.imported_cmds:

        cmd_name = cmd_obj.name
        def d(self, line):
            return getattr(cmd_obj, 'do_'+cmd_name)(line)
        def c(self, text, line, begidx, endidx):
            return getattr(cmd_obj, 'complete_'+cmd_name)(text, line, begidx, endidx)
        def h(self):
            return getattr(cmd_obj, 'help_'+cmd_name)()

        setattr(self.__class__, 'do_'+cmd_name, classmethod(d))
        setattr(self.__class__, 'complete_'+cmd_name, classmethod(c))
        setattr(self.__class__, 'help_'+cmd_name, classmethod(h))


    # def help_cfg(self):
    #     print("\nView and manage master config\n\n   list - show all current config\n   load - reload config from sources\n\nUsage: cfg <action>\n")
    #
    #

    #
    #
    # def do_cfg(self, line):
    #
    #     line_segments = line.split()
    #     if not line_segments:
    #         return
    #
    #     sub_cmd = line_segments[0]
    #
    #     if sub_cmd == 'list':
    #         print("\ncfg: ")
    #         self.pp.pprint(self.cfg)
    #         print("\ncommand tree:")
    #         self.pp.pprint(self.cmd_tree)
    #     elif sub_cmd == 'load':
    #         self.load_cfg()
    #     elif sub_cmd == 'search':
    #         import fnmatch
    #         matches = []
    #         for root, dirnames, filenames in os.walk(os.path.expanduser('~')):
    #             for filename in fnmatch.filter(filenames, '.cmd.yml'):
    #                 matches.append(os.path.join(root, filename))
    #         print(matches)
    #
    #
    #
    # def complete_cfg(self, text, line, begidx, endidx):
    #     return self.completeFromNestedDict(line, self.cmd_tree)
    #
    #
    # def do_test(self, line):
    #     print(self.complete_prj('py', 'prj py', 4, 6))
    #     # self.lastcmd = 'prj'   self, text, line, begidx, endidx
    #     # print self.valueFromNestedDict(line)
    #     # sub_cmd = self.complete_prj   ['prj']['pycardholder']['cmd_class']()
    #     # sub_cmd.cmdloop()


    # def do_test(self, line):
    #     print(self.complete_prj('',  'prj perks ',  4, 5))







if __name__ == '__main__':

    prj = CmdDSH();
    prj.cmdloop_ignore_interrupt()
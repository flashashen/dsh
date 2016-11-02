import cmd
import os
import pprint
import subprocess
import sys
import traceback

import yaml

from commands.cmd_base import CmdBase
from commands.cmd_prj import CmdProject




class CmdDSH(CmdBase, object):


    pp = pprint.PrettyPrinter(indent=4)


    def __init__(self):

        self.cfg = {}
        self.cmd_tree = {'cfg':{'list':'', 'load':''}}
        self.imported_cmds = {'prj':CmdProject()}
        self.load_cfg()
        super(self.__class__, self).__init__()


    def init(self):
        self.load_cfg()

    def load_cfg(self):
        with open(os.path.expanduser('~') + '/.cmd.yml') as cfgfile:
            ycfg = yaml.load(cfgfile.read())
            self.cfg.update(ycfg)
            # self.load_prj_cfg(self.cfg)

            # Initialize imported commands and create do, complete, and help methods for
            # each command, delegating to the command object
            for cmd_name, cmd_obj in self.imported_cmds.iteritems():

                cmd_obj.init(ycfg)

                def d(self, line):
                    return getattr(cmd_obj, 'do_'+cmd_name)(line)
                def c(self, text, line, begidx, endidx):
                    return getattr(cmd_obj, 'complete_'+cmd_name)(text, line, begidx, endidx)
                def h(self):
                    return getattr(cmd_obj, 'help_'+cmd_name)()

                setattr(self.__class__, 'do_'+cmd_name, d)
                setattr(self.__class__, 'complete_'+cmd_name, c)
                setattr(self.__class__, 'help_'+cmd_name, h)

    def help_cfg(self):
        print "\nView and manage master config\n\n   list - show all current config\n   load - reload config from sources\n\nUsage: cfg <action>\n"



    def create_do_shell_command_func(self, cmd):
        def func(self, line):
            print 'executing: {} against line (ignored) {} '.format(cmd, line)
            try:
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                output = e.output
            print output
        return func


    # Cmd class will call this method on the line if it begins with '!'
    def do_shell(self, line):
        try:
            output = subprocess.check_output(line, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            output = e.output
        print output


    def create_help_func(self, str):
        def help_func(self):
            print str
        return help_func



    def do_cfg(self, line):

        line_segments = line.split()
        if not line_segments:
            return

        sub_cmd = line_segments[0]

        if sub_cmd == 'list':
            print "\ncfg: "
            self.pp.pprint(self.cfg)
            print "\ncommand tree:"
            self.pp.pprint(self.cmd_tree)
        elif sub_cmd == 'load':
            self.load_cfg()


    def complete_cfg(self, text, line, begidx, endidx):
        return self.completeFromNestedDict(line, self.cmd_tree)


    def do_test(self, line):
        print self.complete_prj('py', 'prj py', 4, 6)
        # self.lastcmd = 'prj'   self, text, line, begidx, endidx
        # print self.valueFromNestedDict(line)
        # sub_cmd = self.complete_prj   ['prj']['pycardholder']['cmd_class']()
        # sub_cmd.cmdloop()







if __name__ == '__main__':

    prj = CmdDSH();
    prj.init()
    prj.cmdloop_ignore_interrupt()
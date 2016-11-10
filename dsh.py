import cmd
import os
import pprint
import subprocess
import sys
import traceback

import yaml

from commands.cmd_base import CmdBase
from commands.cmd_cfg import CmdConfig
from commands.cmd_docker import CmdDocker
from commands.cmd_ansible import CmdAnsible



class CmdDSH(CmdBase, object):


    def __init__(self):

        # Create config object.
        def on_load(cfg_obj):
            self.configure(cfg_obj)
        self.cfg_obj = CmdConfig(on_load)
        self.cmd = {}
        self.name = 'dsh'

        self.imported_cmds = [CmdDocker(), CmdAnsible(), self.cfg_obj]
        self.prj_objects = { obj.name: obj for obj in self.imported_cmds}

        # Let the config object setup everything
        self.cfg_obj.configure()

        super(self.__class__, self).__init__()



    def configure(self, cfg_obj=None):

        if cfg_obj and 'prj' in cfg_obj.cfg:

            for sub_name, sub_obj in cfg_obj.cfg['prj'].iteritems():
                try:
                    # Load local project config. This allows individual projects to specify their own commands
                    if 'local_dir' in sub_obj:
                        local_dir = os.path.expanduser(sub_obj['local_dir'])
                        fname = local_dir + '/.cmd.yml'
                        if os.path.isfile(fname):
                            with open(fname) as prj_file:

                                ycfg = yaml.load(prj_file.read())

                                # create dynamic subinterpreter class
                                self.prj_objects[sub_name] = self.create_subcmd_class(sub_name, ycfg)()
                                self.prj_objects[sub_name].local_dir = local_dir

                except Exception as e:
                    print("Failed to load config for {}. Error: {}".format(sub_name, str(e)))


        # Configure sub-commands and bind their do,help,complete methods to this main command object
        for cmd_obj in self.prj_objects.values():
            cmd_obj.configure(self.cfg_obj)
            self.load_commands_class(cmd_obj)
            cmd_obj.cfg_obj = self.cfg_obj



    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext) and not a in ['do_EOF','do_shell'] ]



    def do_test(self, line):
        print(self.complete_perks('',  'perks ',  4, 5))


    def load_commands_class(self, cmd_obj):
        """
        Setup do, help, complete methods from submodule to main. Also do any other
        dynamic class setup necessary.

        :param cmd_obj:  The subcommand module object.
        :return: None
        """
        # for cmd_obj in self.imported_cmds:

        cmd_name = cmd_obj.name

        # create a separate cmd dictbb!!!!!!!  this gets setup after cmdproto.
        self.cfg_obj.cmd[cmd_name] = { name: cmd_obj.__getattribute__('do_' + name) for name in cmd_obj.completenames('') }

        def d(self, line):
            segments = line.split()
            if segments:
                subcmd = segments[0]
                try:
                    return getattr(cmd_obj, 'do_' + subcmd)(line)
                except AttributeError as e:
                    print 'no command {}'.format(subcmd)
                except Exception as e:
                    print e
            else:
                cmd_obj.cmdloop_ignore_interrupt()

            # if 'do_' + subcmd in cmd_obj.__dict__:
            #     return getattr(cmd_obj, 'do_' + subcmd)(line)
            # else:
            #     print 'no command {}'.format(subcmd)
        def c(self, text, line, begidx, endidx):

            args = line.split()
            return self.prj_objects[args[0]].generic_class_based_complete(text, ' '.join(line), begidx, endidx)
            # if len(args)>=1 and args[0] in self.prj_objects:
            #     # newline = ' '.join(args[1:])
            #     return self.prj_objects[args[0]].generic_class_based_complete(text, ' '.join(args[1:]), begidx-len(args[0]), endidx-len(args[0]))
            #     #return getattr(self.prj_objects[args[1]],'complete_' + args[1])(self.prj_objects[args[1]], text, ' '.join(args[1:]), begidx-len(args[0]), endidx-len(args[0]))
            # else:
            #     # return self.completeFromNestedDict(line, self.prj_objects)
            #     return getattr(cmd_obj, 'complete_'+line.split()[0])(text, line, begidx, endidx)
        def h(self):
            return getattr(cmd_obj, 'help_'+cmd_name)()

        setattr(self.__class__, 'do_'+cmd_name, classmethod(d))
        setattr(self.__class__, 'complete_'+cmd_name, c)
        setattr(self.__class__, 'help_'+cmd_name, classmethod(h))

        setattr(self.__class__, 'help_'+cmd_name, classmethod(h))


    def get_shell_cmd_context(self):
        return self.cfg_obj.cfg




if __name__ == '__main__':

    prj = CmdDSH();
    prj.cmdloop_ignore_interrupt()
import traceback, sys, os, cmd
import subprocess
import yaml

import cmd_base
from cmd_base import CmdBase

class CmdProject(CmdBase, object):



    def __init__(self):

        self.name = 'prj'
        self.prj_cfg = {}
        self.prj_objects = {}
        super(self.__class__, self).__init__()



    def do_test(self, line):
        print(self.complete_prj('',  'prj perks ',  4, 5))


    def do_prj(self, line):

        args = line.split()
        if not args:
            print('No project specified')
            return

        if args[0] not in self.prj_objects:
            print('Project {} not found'.format(args[0]))
            return

        cmd_obj = self.prj_objects[args[0]]
        if cmd_obj:
            if len(args) == 1:
                cmd_obj.cmdloop()
            else:
                getattr(cmd_obj, 'do_' + args[1])(' '.join(args[1:]))



    def complete_prj(self, text, line, begidx, endidx):

        # cmd, args, l = self.parseline(line)
        # print "{{ cmd: '{}', args '{}', line: '{}' }}".format(cmd, args, l)

        args = line.split()
        if len(args)>1 and args[1] in self.prj_objects:
            # newline = ' '.join(args[1:])
            return self.prj_objects[args[1]].generic_class_based_complete(text, ' '.join(args[1:]), begidx-len(args[0]), endidx-len(args[0]))
            #return getattr(self.prj_objects[args[1]],'complete_' + args[1])(self.prj_objects[args[1]], text, ' '.join(args[1:]), begidx-len(args[0]), endidx-len(args[0]))
        else:
            return self.completeFromNestedDict(line, self.prj_objects)


    def help_prj(self):
        print("\nSelect a command context for code project. Once selected, project specific commands are available\n\nUsage: prj <project name>\n")



    # initialize from master config file
    def configure(self, cfg=None):

        if not cfg or self.name not in cfg:
            return

        self.prj_cfg = cfg[self.name]

        for prj_name, prj_cfg in self.prj_cfg.iteritems():
            try:
                # Load local project config. This allows individual projects to specify their own commands
                if 'local_dir' in prj_cfg:
                    fname = os.path.expanduser(prj_cfg['local_dir']) + '/.cmd.yml'
                    if os.path.isfile(fname):
                        with open(fname) as prj_file:

                            ycfg = yaml.load(prj_file.read())

                            # create dynamic subinterpreter class
                            self.prj_objects[prj_name] = self.create_subcmd_class(prj_name, ycfg)()

            except Exception as e:
                print("Failed to load config for {}. Error: {}".format(prj_name, str(e)))



    def execute_shell_cmd(self, cmd):
        print('executing: ' + cmd)
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            output = e.output

        print(output)



if __name__ == '__main__':

    prj = CmdProject();
    prj.cmdloop_ignore_interrupt()


import traceback, sys, os, cmd
import subprocess
import yaml

from cmd_base import CmdBase

class CmdProject(CmdBase, object):



    def __init__(self):

        self.name = 'prj'
        self.prj_cfg = {}
        self.prj_objects = {}
        super(self.__class__, self).__init__()



    def do_test(self, line):
        print self.complete_prj('p',  'prj py',  4, 5)


    def do_prj(self, line):

        args = line.split()
        if not args:
            print 'No project specified'
            return

        if args[0] not in self.prj_objects:
            print 'Project {} not found'.format(args[0])
            return

        cmd_obj = self.prj_objects[args[0]]
        if cmd_obj:
            if len(args) == 1:
                cmd_obj.cmdloop()
            else:
                cmd_obj.cmdloop()


    # Return project command object names as well as the default commands
    # def completenames(self, text, *ignored):
    #     names = super(self.__class__, self).completenames(text, *ignored)
    #     for name in self.prj_objects:
    #         names.append(name)
    #     names.remove(self.name)
    #     return names;


    def complete_prj(self, text, line, begidx, endidx):
        return self.completeFromNestedDict(line, self.prj_objects)


    def help_prj(self):
        print "\nSelect a command context for code project. Once selected, project specific commands are available\n\nUsage: prj <project name>\n"



    # initialize from master config file
    def init(self, cfg=None):

        if not cfg:
            with open(os.path.expanduser('~') + '/.cmd.yml') as cfgfile:
                cfg = yaml.load(cfgfile.read())

        if not cfg or 'prj' not in cfg:
            return

        self.prj_cfg = cfg['prj']

        for prj_name, prj_cfg in self.prj_cfg.iteritems():
            try:
                # Load local project config. This allows individual projects to specify their own commands
                if 'local_dir' in prj_cfg:
                    fname = os.path.expanduser(prj_cfg['local_dir']) + '/.cmd.yml'
                    if os.path.isfile(fname):
                        with open(fname) as prj_file:

                            ycfg = yaml.load(prj_file.read())

                            # create dynamic subinterpreter class
                            self.prj_objects[prj_name] = self.create_prj_subcmd_class(prj_name, ycfg)()

            except Exception as e:
                print("Failed to load config for {}. Error: {}".format(prj_name, str(e)))


    def create_do_shell_command_func(self, cmd):
        def func(self, line):
            print 'executing: {} against line (ignored) {} '.format(cmd, line)
            try:
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                output = e.output
            print output
        return func


    def create_help_func(self, str):
        def help_func(self):
            print str
        return help_func


    def create_prj_subcmd_class(self, prj_name, prj_dict):

        sub_cmd_class = type("Cmd_" + prj_name, (CmdBase, object), {})

        sub_cmd_class.do_q = self.do_q
        sub_cmd_class.prompt = '({}) '.format(prj_name)

        for key in prj_dict.keys():
            if 'env' == key:
                pass
            else:
                if isinstance(prj_dict[key], dict):
                    setattr(sub_cmd_class, 'do_'+key, classmethod(self.create_do_shell_command_func(prj_dict[key]['cmd'])))
                    setattr(sub_cmd_class, 'help_'+key, classmethod(self.create_help_func(prj_dict[key]['help'])))
                else:
                    setattr(sub_cmd_class, 'do_'+key, classmethod(self.create_do_shell_command_func(prj_dict[key])))
                    setattr(sub_cmd_class, 'help_'+key, classmethod(self.create_help_func('Cmd = {}'.format(prj_dict[key]))))

        return sub_cmd_class



    def execute_shell_cmd(self, cmd):
        print 'executing: ' + cmd
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            output = e.output

        print output



if __name__ == '__main__':

    prj = CmdProject();
    prj.init()
    prj.cmdloop_ignore_interrupt()


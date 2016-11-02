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
        print self.complete_prj('prj ',  'prj ',  4, 4)

    def do_prj(self, line):

        args = line.split()
        if not args:
            print 'No project specified'
            return

        cmd_obj = self.prj_objects[args[0]]
        if cmd_obj:
            if len(args) == 1:
                cmd_obj.cmdloop()
            else:
                cmd_obj.cmdloop()


    def complete_prj(self, text, line, begidx, endidx):
        # print 'complete inputs:', text, line, begidx, endidx
        return self.completeFromNestedDict(line, self.prj_objects)


    def help_prj(self):
        print "put prj help here"



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



    # def completeFromNestedDict(self, line, cmd_dict):
    #
    #     try:
    #         lineSegments = line.split()
    #         if lineSegments:
    #             endsWithWhitespace = line[-1].isspace()
    #         else:
    #             return cmd_dict.keys()
    #
    #         cur_dict = cmd_dict
    #         matched = False
    #         for item in lineSegments:
    #             # skip first segement if it's just the name of the command
    #             if item == self.name:
    #                 pass
    #             elif item in cur_dict:
    #                 matched = True
    #                 cur_dict = cur_dict[item]
    #             else:
    #                 matched = False
    #                 break
    #
    #         if not cur_dict:
    #             return []
    #         elif isinstance(cur_dict,list):
    #             return cur_dict
    #         elif not isinstance(cur_dict,dict):
    #             return []
    #
    #
    #         # If the input ends in whitespace, the the next completion will be
    #         # the whole of the next list in the sequence
    #         if endsWithWhitespace:
    #             return cur_dict.keys()
    #
    #         clist =  [x for x in cur_dict.keys() if x.startswith(lineSegments[-1])]
    #
    #         # If the last segment matched something but there are no completions
    #         # found, then the last item may be complete and we want to return the
    #         # next set of keys
    #         if matched and not clist:
    #             return cur_dict.keys()
    #
    #         return clist
    #
    #     except Exception as e:
    #         print e




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

        sub_cmd_class = type("Cmd_" + prj_name, (cmd.Cmd, object), {})

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

    # quit = False;
    #
    # while not quit:
    #     try:
    #         prj.cmdloop()
    #         quit = True
    #
    #     except KeyboardInterrupt as ke:
    #         pass #print '\n'
    #
    #     except Exception as e:
    #         exc_type, exc_value, exc_traceback = sys.exc_info()
    #         print repr(traceback.format_exception(exc_type, exc_value,
    #                                               exc_traceback))

import cmd
import os
import pprint
import subprocess
import sys
import traceback

import yaml

from commands.cmd_prj import CmdProject


def do_quit(self, args):
    return True


class CmdSimple(cmd.Cmd, object):


    pp = pprint.PrettyPrinter(indent=4)


    def __init__(self):

        self.cfg = {}
        self.cmd_tree = {'cfg':{'list':'', 'load':''}}
        self.imported_cmds = {'prj':CmdProject()}
        self.load_cfg()
        super(self.__class__, self).__init__()




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
                    getattr(cmd_obj, 'do_'+cmd_name)(line)
                def c(self, text, line, begidx, endidx):
                    getattr(cmd_obj, 'complete_'+cmd_name)(text, line, begidx, endidx)
                def h(self, line):
                    getattr(cmd_obj, 'help_'+cmd_name)()

                setattr(self.__class__, 'do_'+cmd_name, d)
                setattr(self.__class__, 'complete_'+cmd_name, c)
                setattr(self.__class__, 'help_'+cmd_name, h)




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



    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.

        """
        # if self.cur_prj != None and not line.startswith('prj'):
        #     return 'prj ' + line

        return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        return stop

    #  override emptyline so last command is not repeated
    def emptyline(self):
        pass



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
        return self.completeFromNestedDict(line)


    def do_test(self, line):
        print self.complete_prj('prj ', line, 0, 0)
        # self.lastcmd = 'prj'   self, text, line, begidx, endidx
        # print self.valueFromNestedDict(line)
        # sub_cmd = self.complete_prj   ['prj']['pycardholder']['cmd_class']()
        # sub_cmd.cmdloop()



    def completeFromArrays(self, line, argLists):

        lineSegments = line.split()
        numArgsInput = len(lineSegments)-1;
        endsWithWhitespace = line[-1].isspace()


        # If the input ends in whitespace, the the next completion wil be
        # the whole of the next list in the sequence
        if endsWithWhitespace:
            if numArgsInput >= len(argLists):
                return []
            return argLists[numArgsInput][:]


        # The input cursor is still at the end of the command. Wait for an
        # initial whitespace before returning any completions. Also test
        # for extra arguments
        if numArgsInput == 0 or numArgsInput > len(argLists):
            return []


        # Return any matching values from the relevant list
        return [ f
                 for f in argLists[numArgsInput-1]
                 if f.startswith(lineSegments[-1])
                 ]


    def valueFromNestedDict(self, line, cmd_dict = None):

        # By default, use the lastcmd (first segment) to get the command tree
        # for this command
        if not cmd_dict:
            cmd_dict = self.cmd_tree[self.lastcmd.split()[0]]

        lineSegments = line.split()
        val = cmd_dict
        for item in lineSegments:
            if item in val:
                val = val[item]
            else:
                break

        if not isinstance(val, dict):
            return val
        else:
            return None


    def completeFromNestedDict(self, line, cmd_dict = None):

        # print 'calling completeFromNestedDict (cmd = {}, line = {}) on {}'.format(self.lastcmd, line, str(cmd_dict))

        # By default use the parsed command string as the key to the command tree dict
        if not cmd_dict:
            cmd_dict = self.cmd_tree

        # print 'running completeFromNestedDict on ' + str(cmd_dict)

        try:
            lineSegments = line.split()
            if lineSegments:
                endsWithWhitespace = line[-1].isspace()
            else:
                return cmd_dict.keys()

            cur_dict = cmd_dict
            matched = False
            for item in lineSegments:
                if item in cur_dict:
                    matched = True
                    cur_dict = cur_dict[item]
                else:
                    matched = False
                    break

            if not cur_dict:
                return []
            elif isinstance(cur_dict,list):
                return cur_dict
            elif not isinstance(cur_dict,dict):
                return []


            # If the input ends in whitespace, the the next completion will be
            # the whole of the next list in the sequence
            if endsWithWhitespace:
                return cur_dict.keys()

            clist =  [x for x in cur_dict.keys() if x.startswith(lineSegments[-1])]

            # If the last segment matched something but there are no completions
            # found, then the last item may be complete and we want to return the
            # next set of keys
            if matched and not clist:
                return cur_dict.keys()

            return clist

        except Exception as e:
            print e




if __name__ == '__main__':

    while 1:
        try:
            CmdSimple().cmdloop()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        except KeyboardInterrupt as ke:
            print '\n'
            break

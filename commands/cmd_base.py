import traceback, sys, os, cmd, yaml
import subprocess
import types
from cmd_proto import CmdProto

class CmdBase(cmd.Cmd, object):


    def configure(self, cfg_obj=None):
        pass

    #  override emptyline so last command is not repeated
    def emptyline(self):
        pass

    def do_q(self, line):
        return True

    def do_EOF(self, line):
        print('\n')
        return True

    # Keep EOF and q from cluttering help
    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext) and not a in ['do_EOF','do_q','do_help','do_shell'] ]


    def generic_class_based_complete(self, text, line, begidx, endidx):
        # print "complete. text = '{}' line = '{}', {} {}".format(text, line, begidx, endidx)
        return [c for c in self.completenames(text, line, 0, 0) if 'do_'+c not in STANDARD_DO_METHODS and c != self.name]


# deploy_w_role:
#     help: 'Try specifying a sub command from another module - to deploy ingo'
#     cmd:
#         ans.role:
#             role: app_pycardholder
#             target: fsd-docker01.an.local"



    # def create_dict_command_func(self, configured_cmd):
    #
    #     if isinstance(configured_cmd, dict):
    #         for key, cmd_spec in  configured_cmd.iteritems():
    #
    #
    #         setattr(sub_cmd_class, 'do_'+key, self.create_dict_command_func(sdict[key]['cmd']))
    #         setattr(sub_cmd_class, 'help_'+key, self.create_help_func(sdict[key]['help']))
    #     else:
    #
    # def func(self, line):
    #         # !! add delegation to other commands here. in progress
    #         # if params:
    #         #     print 'params passed to do function: {}'.format(cmd_dict)
    #         # cmd_segments = configured_cmd.split('.')
    #         # if cmd_segments[0] in self.cfg_obj.cmd:
    #         #     if len(cmd_segments) > 1:
    #         #         self.cfg_obj.cmd[cmd_segments[1]](line)
    #         #     print 'command found in {}'.format(cmd_segments[0])
    #         #        self.cfg_obj.cmd[self.name][]
    #         self.execute(configured_cmd, True)
    #     return func

    def create_command_func(self, configured_cmd):

        # if isinstance(configured_cmd, dict):
        #     return CmdProto.from_dict('test', configured_cmd, self.cfg_obj.cmd_tree, self.cfg_obj.cfg)

        def func(self, line):
            self.execute(configured_cmd, line, True)
        return func

    def create_help_func(self, str):
        def help_func(self):
            print(str)
        return help_func


    def create_subcmd_class(self, sname, sdict):

        sub_cmd_class = type("Cmd_" + sname, (CmdBase, object), {})

        sub_cmd_class.name = sname
        sub_cmd_class.do_q = self.do_q
        sub_cmd_class.prompt = '({}) '.format(sname)

        for key in sdict.keys():
            if 'env' == key:
                pass
            if 'dsh' == key:
                pass
            else:
                cp = CmdProto.from_dict_with_CmdBase_obj(sname, key, sdict[key], self.cfg_obj)
                cp.setup_Cmd_methods(sub_cmd_class)

                # if isinstance(sdict[key], dict):
                #     cp = CmdProto.from_dict_with_CmdBase_obj(sname, key, sdict[key], self.cfg_obj)
                #     cp.setup_Cmd_methods(sub_cmd_class)
                #     # setattr(sub_cmd_class, 'do_'+key, cp.as_cmd_do_function())
                #     # setattr(sub_cmd_class, 'help_'+key, self.create_help_func(sdict[key]['help']))
                # else:
                #     setattr(sub_cmd_class, 'do_'+key, self.create_command_func(sdict[key]))
                #     setattr(sub_cmd_class, 'help_'+key, self.create_help_func('Cmd = {}'.format(sdict[key])))

        # def c(self, text, line, begidx, endidx):
        #     print "dyn complete. text = '{}' line = '{}', {} {}".format(text, line, begidx, endidx)
        #     # parse = self.parseline(line)
        #     # print 'parse: ', parse[0], parse[1], parse[2]
        #     return self.generic_class_based_complete(self, text, line, begidx, endidx)

        # setattr(sub_cmd_class, 'complete_'+sname, self.generic_class_based_complete)

        return sub_cmd_class




    def cmdloop_ignore_interrupt(self):

        quit = False;

        while not quit:
            try:
                self.cmdloop()
                quit = True

            except KeyboardInterrupt as ke:
                print('\n')

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback)))


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


    def completeFromNestedDict(self, line, cmd_dict):

        try:
            lineSegments = line.split()
            if lineSegments:
                endsWithWhitespace = line[-1].isspace()
            else:
                return cmd_dict.keys()

            cur_dict = cmd_dict
            matched = False
            for item in lineSegments:
                # skip first segement if it's just the name of the command. 'name' is a new
                # sublcass attribute that subclasses may not provide
                if hasattr(self, 'name') and item == self.name:
                    pass
                elif item in cur_dict:
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
            print(e)



    # Cmd class will call this method on the line if it begins with '!'
    def do_shell(self, line, print_to_console=True):
        self.execute(line, None, print_to_console)


    def __execute_with_running_output(self, command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Poll process for new output until finished
        while True:
            nextline = process.stdout.readline()
            if nextline == '' and process.poll() is not None:
                break
            sys.stdout.write(nextline)
            sys.stdout.flush()

        output = process.communicate()[0]
        exitCode = process.returncode

        if (exitCode == 0):
            return output
        else:
            raise Exception(command, exitCode, output)


    def flatten_cmd(self, cmds, cmd_tree):

        if isinstance(cmds, str) or isinstance(cmds, CmdProto):
            return [cmds]

        cmd_list = []
        if isinstance(cmds, list):
            for item in cmds:
                cmd_list.extend(self.flatten_cmd(item, cmd_tree))

        elif isinstance(cmds, dict):
            # Recursive call to iterate over dict items though only one is expected
            for key, item in cmds.iteritems():

                # dict could now be the whole sub cmd spec with 'cmd' as an item
                if isinstance(item, dict):
                    cmd_list.extend(self.flatten_cmd(item, cmd_tree))
                elif isinstance(item, str):
                    # The value is a string so this is a command in the form of <cmd.subcmd>:<args line>
                    cmd_segments = key.split('.')
                    if len(cmd_segments) > 1:
                        if cmd_segments[0] in cmd_tree:
                            cmd_list.append(CmdProto.from_CmdBase_instance_method(cmd_tree[cmd_segments[0]][cmd_segments[1]], cmds[key]))
                            # cmd_list.append(cmd_tree[cmd_segments[0]][cmd_segments[1]])
                            # args = cmds[key]
                        else:
                            print "root level command not found: {}".format(cmd_segments[0])
                    else:
                        print 'no self cmd supported here'
                else:
                    print 'unexpected value type for obj %s' %item

        return cmd_list



    def execute(self, cmds, args, print_to_console=True):

        if 'local_dir' in self.__dict__ and self.local_dir:
            od = os.getcwd()
            os.chdir(self.local_dir)

        try:

            cmd_list = self.flatten_cmd(cmds, self.cfg_obj.cmd)

            # print('\n')
            output = None

            for index, c in enumerate(cmd_list):

                if isinstance(c, CmdProto):
                    c.execute(args)
                elif type(c) == types.MethodType:
                    c(args)
                else:
                    # try:
                    c = c.format(cfg=self.get_shell_cmd_context())
                    # except:
                    #     c = c.format(cfg=self.get_shell_cmd_context())
                    print('executing: {}\n'.format(c))
                    output = self.__execute_with_running_output(c)

        except AttributeError as ae:
            output = ae.message
        except subprocess.CalledProcessError as e:
            output = e.output

        finally:
            if 'local_dir' in self.__dict__ and self.local_dir:
                os.chdir(od)

        if output and print_to_console:
            print output

        return output



    def get_shell_cmd_context(self):
        return self.cfg_obj.cfg


    def create_help_func(self, str):
        def help_func(self):
            print(str)
        return help_func



    # def completeFromArrays(self, line, argLists):
    #
    #     lineSegments = line.split()
    #     numArgsInput = len(lineSegments)-1;
    #     endsWithWhitespace = line[-1].isspace()
    #
    #
    #     # If the input ends in whitespace, the the next completion wil be
    #     # the whole of the next list in the sequence
    #     if endsWithWhitespace:
    #         if numArgsInput >= len(argLists):
    #             return []
    #         return argLists[numArgsInput][:]
    #
    #
    #     # The input cursor is still at the end of the command. Wait for an
    #     # initial whitespace before returning any completions. Also test
    #     # for extra arguments
    #     if numArgsInput == 0 or numArgsInput > len(argLists):
    #         return []
    #
    #
    #     # Return any matching values from the relevant list
    #     return [ f
    #              for f in argLists[numArgsInput-1]
    #              if f.startswith(lineSegments[-1])
    #              ]


    def add_default_command_delegation(self):

        # Add default do method
        def d(self, line):
            try:
                cmd_name = line.split()[0]
                func = getattr(self, 'do_'+cmd_name)
                if not func:
                    print "no command '{}'".format(cmd_name)
                    return
                func(line)
            except Exception as e:
                print e.message
        setattr(self.__class__, 'do_' + self.name, d)

        # Add default complete method
        def c(self, text, line, begidx, endidx):
            return self.generic_class_based_complete(text, line, begidx, endidx)
        setattr(self.__class__, 'complete_' + self.name, c)


STANDARD_DO_METHODS = [f for f in dir(CmdBase) if f.startswith('do_')]



def cfg_expanduser(obj, recursion = 0):

    if isinstance(obj, str):
        return os.path.expanduser(obj)

    elif isinstance(obj, list) and recursion < 10:
        return [cfg_expanduser(x, recursion+1) for x in obj]

    elif isinstance(obj, dict) and recursion < 10:
        return { key: cfg_expanduser(obj[key], recursion+1) for key in obj }
        # for key in dict:
        #     dict[key] = cfg_expanduser(dict[key], recursion+1)

    else:
        return obj




#
#
# def generic_complete(cmd_obj, text, line, begidx, endidx):
#     # print "complete. text = '{}' line = '{}', {} {}".format(text, line, begidx, endidx)
#     return [c for c in cmd_obj.completenames(text, line, 0, 0) if 'do_'+c not in STANDARD_DO_METHODS and c != cmd_obj.name]
#     #
#     # cmd, args, foo = cmd_obj.parseline(line)
#     # if cmd == '':
#     #     compfunc = cmd_obj.completedefault
#     # else:
#     #     try:
#     #         compfunc = getattr(cmd_obj, 'complete_' + cmd)
#     #     except AttributeError:
#     #         compfunc = cmd_obj.completedefault
#     #
#     # matches = compfunc(text, line, begidx, endidx)
#     # return [c for c in matches if 'do_'+c not in STANDARD_DO_METHODS and c != cmd_obj.name]

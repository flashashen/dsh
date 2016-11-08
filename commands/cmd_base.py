import traceback, sys, os, cmd, yaml
import subprocess


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



    def create_command_func(self, configured_cmd):
        def func(self, line):
            self.execute(configured_cmd, True)
        return func
        # def func(self, line, print_to_console=True):
        #
        #     if isinstance(cmd, str):
        #         cmd_list = [cmd]
        #     else:
        #         cmd_list = cmd
        #
        #
        #     if self.local_dir:
        #         od = os.getcwd()
        #         os.chdir(self.local_dir)
        #
        #     try:
        #
        #         print('\n')
        #         for index, c in enumerate(cmd_list):
        #             c = c.format(cfg=self.get_shell_cmd_context())
        #             print('{}. executing: {}\n'.format(index+1, c))
        #             output = subprocess.check_output(c, stderr=subprocess.STDOUT, shell=True)
        #
        #     except AttributeError as ae:
        #         output = ae.message
        #     except subprocess.CalledProcessError as e:
        #         output = e.output
        #
        #     finally:
        #         if od:
        #             os.chdir(od)
        #
        #     if print_to_console:
        #         print output
        #
        #     return output
        #
        # return func


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
                if isinstance(sdict[key], dict):
                    setattr(sub_cmd_class, 'do_'+key, self.create_command_func(sdict[key]['cmd']))
                    setattr(sub_cmd_class, 'help_'+key, self.create_help_func(sdict[key]['help']))
                else:
                    setattr(sub_cmd_class, 'do_'+key, self.create_command_func(sdict[key]))
                    setattr(sub_cmd_class, 'help_'+key, self.create_help_func('Cmd = {}'.format(sdict[key])))

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
        self.execute(line, print_to_console)


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


    def execute(self, line, print_to_console=True):

        if isinstance(line, str):
            cmd_list = [line]
        else:
            cmd_list = line


        if 'local_dir' in self.__dict__ and self.local_dir:
            od = os.getcwd()
            os.chdir(self.local_dir)

        try:

            print('\n')
            for index, c in enumerate(cmd_list):
                try:
                    c = c.format(cfg=self.get_shell_cmd_context())
                except:
                    c = c.format(cfg=self.get_shell_cmd_context())
                print('{}. executing: {}\n'.format(index+1, c))
                output = self.__execute_with_running_output(c)
                # output = subprocess.check_output(c, stderr=subprocess.STDOUT, shell=True)

        except AttributeError as ae:
            output = ae.message
        except subprocess.CalledProcessError as e:
            output = e.output

        finally:
            if 'local_dir' in self.__dict__ and self.local_dir:
                os.chdir(od)

        if print_to_console:
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

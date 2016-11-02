import traceback, sys, os, cmd
import subprocess
import yaml


class CmdBase(cmd.Cmd, object):


    #  override emptyline so last command is not repeated
    def emptyline(self):
        pass

    def do_q(self, line):
        return True

    def do_EOF(self, line):
        print '\n'
        return True

    # Keep EOF and q from cluttering help
    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext) and not a in ['do_EOF','do_q'] ]


    def cmdloop_ignore_interrupt(self):

        quit = False;

        while not quit:
            try:
                self.cmdloop()
                quit = True

            except KeyboardInterrupt as ke:
                print '\n'

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback))


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
            print e



    #
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
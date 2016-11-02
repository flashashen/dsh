import traceback, sys, os, cmd
import subprocess
import yaml


class CmdBase(cmd.Cmd, object):


    #  override emptyline so last command is not repeated
    def emptyline(self):
        pass

    def do_q(self, line):
        return True

    def help_q(self):
        print 'quit the current context'


    def cmdloop_ignore_interrupt(self):

        quit = False;

        while not quit:
            try:
                self.cmdloop()
                quit = True

            except KeyboardInterrupt as ke:
                pass #print '\n'

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback))


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
                # skip first segement if it's just the name of the command
                if item == self.name:
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

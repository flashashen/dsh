



import subprocess, sys
def execute_with_running_output(command, ctx):

    command = command.format(cfg=ctx)
    print('executing: {}\n'.format(command))

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




class CmdProto():

    def __init__(self, name):

        self.name = name
        self.help = "No help"

        # use a function to access ctx so it can be overridden
        self._env = {}
        def ge():
            return self._env
        self.get_env = ge

        # use a function to access cmds so it can be overridden
        self._cmd_tree = {}
        def gc():
            return self._cmd_tree
        self.get_cmd_tree = gc


        # default to shell executor for now
        self.executor = self.get_shell_executor()


    def execute(self, str_input):
        self.executor(str_input, self.get_env(), self.get_cmd_tree())



    def get_shell_executor(self, cmd_string=None):
        def executor(input, env, cmd_tree):
            return execute_with_running_output(
                cmd_string if cmd_string else input,
                env)
        return executor



    def as_cmd_do_function(self):
        # return an object that fits the Cmd do_ method signature but delegates execution
        # to this CmdProto object. The 'obj' parameter makes it eligible to be an instance
        # method but no instance data will be necessary since its provided when this cmd_proto
        # object is constructed
        def f(obj, line):
            return self.execute(line)
        return f


    def setup_Cmd_methods(self, target_class):

        setattr(target_class, 'do_'+self.name, self.as_cmd_do_function())

        def help_func(obj):
            print(self.help)
        setattr(target_class, 'help_'+self.name, help_func)


    @staticmethod
    def from_CmdBase_instance_method(cmd_method, args):
        """
        Create a CmdProto object from a bound Cmd do_* method which already has context

        :param cmd_method:  CmdBase instance method
        :return: CmdProto object ready for execution
        """
        cp = CmdProto('cmd_method')
        def executor(input, env, cmd_tree):
            # ignore contex since method already is bound to a context. Append inputs to the given args.
            return cmd_method(args + " " + input)
        cp.executor = executor
        return cp


    @staticmethod
    def from_python_formatted_shell_cmd_method(cmd_string,  env):
        """
        Create a CmdProto object from a python format string which will be formatted into
        a shell command string.

        :param cmd_string:  CmdBase instance method
        :param env:  dict with subsitution variables. nesting is ok
        :return: CmdProto object ready for execution
        """
        cp = CmdProto('shell_cmd')
        cp._env = env
        cp.executor = cp.get_shell_executor(cmd_string)
        return cp


    @staticmethod
    def from_dict_with_CmdBase_obj(name, spec, cfg_obj):

        # provide cmd and env getters based on the CmdBase config object.
        # The config object is not fully build yet so use a lazy init strategy
        def cmds_get():
            return cfg_obj.cmd
        def env_get():
            return cfg_obj.cfg

        return CmdProto.from_dict_with_lazy_init(name, spec, cmds_get, env_get)


    @staticmethod
    def from_dict_with_lazy_init(name, spec, cmds_get, env_get):

        cp = CmdProto(name)
        cp.get_env = env_get
        cp.get_cmd_tree = cmds_get

        # add a cmd_list attribute to set on lazy init during execution
        cp._cmd_list = None

        if 'help' in spec:
            cp.help = spec['help']

        if 'cmd' in spec:
            cmds = spec['cmd']

        # define an execute that will build the command list only on first execution
        # this is necessary because CmdBase uses classes to create the cmd list and
        # this method is called while classes are still being loaded.
        def executor(input, env, cmd_tree):

            # cmds and cp are bound via closure
            if not cp._cmd_list:
                cp._cmd_list = flatten_cmd(cmds, cmd_tree, env)
            for cmd in cp._cmd_list:
                cmd.execute(input)

        cp.executor = executor
        return cp




def flatten_cmd(cmds, cmd_tree, env):

    if isinstance(cmds, str):
        return [CmdProto.from_python_formatted_shell_cmd_method(cmds, env)]

    cmd_list = []
    if isinstance(cmds, list):
        for item in cmds:
            cmd_list.extend(flatten_cmd(item, cmd_tree, env))

    elif isinstance(cmds, dict):
        # Recursive call to iterate over dict items though only one is expected
        for key, item in cmds.iteritems():

            # dict could now be the whole sub cmd spec with 'cmd' as an item
            if isinstance(item, dict):
                cmd_list.extend(flatten_cmd(item, cmd_tree, env))
            elif isinstance(item, str):
                # The value is a string so this is a command in the form of <cmd.subcmd>:<args line>
                cmd_segments = key.split('.')
                if len(cmd_segments) > 1:
                    if cmd_segments[0] in cmd_tree:
                        cmd_list.append(CmdProto.from_CmdBase_instance_method(cmd_tree[cmd_segments[0]][cmd_segments[1]], cmds[key]))
                    else:
                        print "root level command not found: {}".format(cmd_segments[0])
                else:
                    print 'no self cmd supported here'
            else:
                print 'unexpected value type for obj %s' %item

    return cmd_list



import cmd_base
from cmd_base import CmdBase

class CmdDocker(CmdBase, object):


    def __init__(self):
        super(self.__class__, self).__init__()
        self.name = 'dock'
        cmd_base.add_default_command_delegation(self, self.name)


    def do_info(self, line):
        self.do_shell('docker-machine active')


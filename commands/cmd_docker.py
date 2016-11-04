import json
import cmd_base
from cmd_base import CmdBase

class CmdDocker(CmdBase, object):


    def __init__(self):
        super(self.__class__, self).__init__()
        self.name = 'dock'
        cmd_base.add_default_command_delegation(self, self.name)


    def do_vm(self, line):
        dm_info = self.get_vm_info()
        print 'name:\t', dm_info['Name']
        # print dm_info['Driver']['MachineName']
        print 'ip:\t', dm_info['Driver']['IPAddress']
        print 'port:\t', dm_info['Driver']['SSHPort']
        print 'user:\t', dm_info['Driver']['SSHUser']
        print 'key  :\t', dm_info['Driver']['SSHKeyPath']


    def do_refresh_vm(self, line):
        dm_info = self.get_vm_info()
        self.do_shell('ansible-playbook playbooks/refresh_docker_machine.yml -i "{}," -vvvv -u "{}" --become --private-key=/app/id_rsa')

    def do_test(self, line):
        print 'test '



    def get_vm_info(self):
        return json.loads(self.do_shell('docker-machine inspect', False))
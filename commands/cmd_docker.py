import json
import cmd_base
from cmd_base import CmdBase

class CmdDocker(CmdBase, object):


    def __init__(self):
        super(self.__class__, self).__init__()
        self.name = 'dkr'
        self.add_default_command_delegation()


    def do_vm(self, line):
        dm_info = self.get_vm_info()
        print 'name:\t', dm_info['Name']
        print 'status:\t', dm_info['Status']
        # print dm_info['Driver']['MachineName']
        print 'ip:\t', dm_info['Driver']['IPAddress']
        print 'port:\t', dm_info['Driver']['SSHPort']
        print 'user:\t', dm_info['Driver']['SSHUser']
        print 'key  :\t', dm_info['Driver']['SSHKeyPath']


    def do_refresh_vm(self, line):
        dm_info = self.get_vm_info()
        cmd = 'ansible-playbook playbooks/refresh_docker_machine.yml -i "{}," -vvvv -u "{}" --become --private-key={}'.format(
            dm_info['Driver']['IPAddress'], dm_info['Driver']['SSHUser'], dm_info['Driver']['SSHKeyPath'])
        print cmd
        self.do_shell(cmd)


    def get_vm_info(self):
        info = json.loads(self.do_shell('docker-machine inspect', False))
        info['Status'] = self.do_shell('docker-machine status', False).strip()
        return info
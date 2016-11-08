import cmd_base
from cmd_base import CmdBase

class CmdAnsible(CmdBase, object):


    def __init__(self):
        super(self.__class__, self).__init__()
        self.name = 'ans'
        self.add_default_command_delegation()


    cmd_run_role = " ansible-playbook -i {cfg[ans][inventory_file]} {cfg[ans][playbook_dir]}/run_role.yml \
                --vault-password-file={cfg[ans][vault_pass_file]} \
                -e 'ansible_ssh_user={cfg[ans][ssh_user]}' -vvvv -u 'ansible' \
                --private-key={cfg[ans][ssh_key]} \
                --become --become-user=root \
                -e  'ROLE={cfg[scratch][ROLE]}' -e 'TARGET=fsd-docker01.an.local'"

    def do_role(self, line):
        self.cfg_obj.cfg['scratch'] = {'ROLE':line.split()[-1]}
        self.execute(self.cmd_run_role)
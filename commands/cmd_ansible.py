import cmd_base
from cmd_base import CmdBase

class CmdAnsible(CmdBase, object):


    def __init__(self):
        super(self.__class__, self).__init__()
        self.name = 'ans'
        self.add_default_command_delegation()


    cmd_rcmd = "ansible all -i {cfg[ans][inventory_file]} \
        -e 'ansible_ssh_user={cfg[ans][ssh_user]}' -u '{cfg[ans][ssh_user]}' \
        --become --become-user=root --private-key={cfg[ans][ssh_key]} -m shell -a '{cfg[scratch][LINE]}' --limit={cfg[scratch][TARGET]}"


    cmd_run_role = " ansible-playbook -i {cfg[ans][inventory_file]} {cfg[ans][playbook_dir]}/run_role.yml \
                --vault-password-file={cfg[ans][vault_pass_file]} \
                -e 'ansible_ssh_user={cfg[ans][ssh_user]}' -u '{cfg[ans][ssh_user]}' \
                --private-key={cfg[ans][ssh_key]} \
                --become --become-user=root \
                -e  'ROLE={cfg[scratch][ROLE]}'"

    cmd_role_part_target = " -e 'TARGET={cfg[scratch][TARGET]}'"


    def help_rcmd(self):
        print 'Usage: rcmd target_host arg0 [arg1[,argN]]'

    def do_rcmd(self, line):
        args = line.split()
        if args:
            try:
                cmd_string = self.cmd_rcmd
                self.cfg_obj.cfg['scratch'] = {'TARGET':args[0]}
                self.cfg_obj.cfg['scratch']['LINE'] = ' '.join(args[1:])
                self.execute(cmd_string, '')
            finally:
                self.cfg_obj.cfg['scratch'] = {}


    def help_role(self):
        print 'Usage: role rolename [target host]'

    def do_role(self, line):
        args = line.split()
        if args:
            try:
                cmd_string = self.cmd_run_role
                self.cfg_obj.cfg['scratch'] = {'ROLE':args[0]}
                if len(args) > 1:
                    cmd_string += self.cmd_role_part_target
                    self.cfg_obj.cfg['scratch']['TARGET'] = args[1]

                self.execute(cmd_string, line)
            finally:
                self.cfg_obj.cfg['scratch'] = {}
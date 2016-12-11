import os
import cmd_base
from cmd_base import CmdBase

class CmdAnsible(CmdBase, object):


    def __init__(self):
        super(self.__class__, self).__init__()
        self.name = 'ans'
        self.add_default_command_delegation()

    # -i {cfg[ans][inventory_file]}  removed in favor of local ansible config files. can still be specified via cmd or default cfg

    cmd_play = "ansible-playbook -i {cfg[ans][inventory_file]} {cfg[scratch][PLAYBOOK]} \
        -e 'ansible_ssh_user={cfg[ans][ssh_user]}' -e 'ansible_ssh_pass={cfg[ans][ssh_pass]}' \
        --vault-password-file={cfg[ans][vault_pass_file]} --limit={cfg[scratch][TARGET]} \
        -e 'ansible_sudo_pass={cfg[ans][ssh_pass]}' {cfg[scratch][LINE]}"


    cmd_rcmd = "ansible all -e 'ansible_ssh_user={cfg[ans][ssh_user]}' -u '{cfg[ans][ssh_user]}' \
        --become --become-user=root --private-key={cfg[ans][ssh_key]} -m shell -a '{cfg[scratch][LINE]}' --limit={cfg[scratch][TARGET]}"


    # cmd_run_role = " ansible-playbook {cfg[ans][playbook_dir]}/run_role.yml \
    #             --become --become-user=root \
    #             -e  'ROLE={cfg[scratch][ROLE]}'"

    # --private - key = {cfg[ans][ssh_key]}
    cmd_run_role = " ansible-playbook -vvv " + os.path.join(os.path.dirname(os.path.realpath(__file__)),'resources', 'run_role.yml') +  " \
        -i {cfg[ans][inventory_file]}  --vault-password-file={cfg[ans][vault_pass_file]} \
        -e 'ansible_ssh_user={cfg[ans][ssh_user]}' -u '{cfg[ans][ssh_user]} ' -e 'ansible_ssh_pass={cfg[ans][ssh_pass]}' \
        --become --become-user=root \
        -e  'ROLE={cfg[scratch][ROLE]}'"

    cmd_role_part_target = " -e 'TARGET={cfg[scratch][TARGET]}'"



    def help_play(self):
        print 'Usage: play playbook host|group [arg1[,argN]]'

    def do_play(self, line):
        args = line.split()
        if args:
            try:
                playbook = os.path.join(self.cfg_obj.cfg['ans']['playbook_dir'], args[0])
                # print 'playbook {}'.format(playbook)
                cmd_string = self.cmd_play
                self.cfg_obj.cfg['scratch'] = {'PLAYBOOK':playbook}
                self.cfg_obj.cfg['scratch']['TARGET'] = args[1]
                self.cfg_obj.cfg['scratch']['LINE'] = ' '.join(args[2:])
                self.execute(cmd_string, '')
            finally:
                self.cfg_obj.cfg['scratch'] = {}




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
        print 'Usage: role rolename target'

    def do_role(self, line):
        args = line.split()
        if len(args) < 2:
            self.help_role()
            return
        if args:
            try:
                cmd_string = self.cmd_run_role
                self.cfg_obj.cfg['scratch'] = {'ROLE':args[0]}
                if len(args) > 1:
                    cmd_string += self.cmd_role_part_target
                    self.cfg_obj.cfg['scratch']['TARGET'] = args[1]

                print cmd_string
                self.execute(cmd_string, line)
            finally:
                self.cfg_obj.cfg['scratch'] = {}


    def do_edit_inv(self, line):
        self.do_edit_file(self.cfg_obj.cfg['ans']['inventory_file'])

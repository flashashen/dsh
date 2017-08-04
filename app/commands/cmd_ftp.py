from cmd_base import CmdBase



class CmdFtp(CmdBase, object):

    def __init__(self):
            import pysftp
            super(self.__class__, self).__init__()
            self.name = 'ftp'
            self.add_default_command_delegation()


            self.sftp = None
            self.cwd_file_listing = None


    def do_connect(self, line):

        try:
            self.sftp.close()
            self.stdout.write('Prior connection closed\n')
            self.prompt = '(ftp)'
        except:
            pass

        self.sftp = pysftp.Connection(self.host, username=self.username, password=self.password)
        self.stdout.write('Connection opened\n')
        self.prompt = '({})'.format(self.host)
        self.cwd_file_listing = self.sftp.listdir()

    def do_close(self, line):

        try:
            self.sftp.close()
            self.stdout.write('Connection closed\n')
        except:
            pass
        self.sftp = None
        self.prompt = '(ftp)'


    def do_ls(self, line):
        path = line.strip()
        if path:
            print self.sftp.listdir(path)
        else:
            print self.sftp.listdir()


    def do_pwd(self, line):
        print(self.sftp.pwd)

    def do_cd(self, line):
        self.sftp.chdir(line.strip())
        self.cwd_file_listing = self.sftp.listdir()

    def complete_cd(self, text, line, begidx, endidx):
        return [x for x in self.cwd_file_listing if x.startswith(text)]

    def do_get(self, line):
        print((self.sftp.get(line.strip())))

    def complete_get(self, text, line, begidx, endidx):
        return [x for x in self.cwd_file_listing if x.startswith(text)]

    def do_put(self, line):
        print(self.sftp.put(line.strip()))
        self.cwd_file_listing = self.sftp.listdir()


    def help_rcmd(self):
        print 'Usage: rcmd target_host arg0 [arg1[,argN]]'

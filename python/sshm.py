#! /bin/env  python2
#encoding:utf8
import string
import re
import os
def list_header(  ):
    for letter in string.uppercase:
        yield letter + '.'

class color_out:
    def __init__(self):
        self.color_switch = True

    def on(self):
        self.color_switch = True
    def off(self):
        self.color_switch = False

    def black(self,s):  return self.__color(30, s)
    def red(self,s):    return self.__color(31, s)
    def green(self,s):  return self.__color(32, s)
    def yellow(self,s): return self.__color(33, s)
    def blue(self,s):   return self.__color(34, s)
    def purple(self,s): return self.__color(35, s)
    def white(self,s):  return self.__color(37, s)

    def __color(self, color_int, s):
        if self.color_switch:
            return  "%s[%d;2m%s%s[0m" %(chr(27), color_int, s, chr(27))  
        else:
            return  s
          
    def highlight(self,s):  
        if self.color_switch:
            return  "%s[30;2m%s%s[1m"%(chr(27), s, chr(27))
        else:
            return  s

color=color_out( )

class item:
    root='root'
    ip=''
    des=''
    port=22
    password=''
class _sshrc:
    def __init__( self ):
        self.get_lines( )
        self.get_items( )
    def show_remote( self ):
        header = list_header()
        i = 0
        for item in self.items:
            i = i + 1 
            context = header.next()+ item.ip.ljust(16)+ str(item.port).ljust(7)+ item.des
            if i%2  == 0:
                context = color.blue(context)
            else:
                context = color.red(context)
            print context

    def get_lines( self ):
        sshrc = os.path.join(os.environ[ "HOME" ], ".sshrc")
        f=open( sshrc )
        lines= f.readlines( )
        f.close( )
        self.lines = lines
        return lines

    def get_items( self ):

        items=[  ]

        for line in self.lines:

            line= line[ 0:-1 ]
            tmp = item( )
            line_split = line.split( )
            if len(line_split) > 3:

                tmp.root=line_split[ 0 ]
                tmp.ip=line_split[ 1 ]
                tmp.port=int(line_split[ 2 ])
                tmp.password = line_split[ 3 ]

            if len(line_split) > 4:
                tmp.des=' '.join(line_split[ 4: ])
            items.append( tmp )


        self.items=items
        return items
    def get_item( self, index ):
        return self.items[ index ]

    def get_item_by_host( self, host):
        for item in self.items:
            if item.ip == host:
                return item
        return None

class _sshm( object ):
    def __init__( self ):
        self.sshrc= _sshrc( )
        self.default_cmd = self.ssh


    def select( self ):
        cmd = raw_input( "\n++Select the remote or Add new remote or Type cmd[rtol, ltor]\n>>")
        self.cmd_header( cmd )

    def cmd_header( self, cmd ):
        cmd_seq= cmd.split( )
        cmd = cmd_seq[ 0 ]

        if cmd == 'exit':
            return 0

        if cmd == 'del':
            if len( cmd_seq ) < 2:
                return -1
            #TODO
        if cmd == 'sftp':
            if len( cmd_seq ) < 2 or len(cmd_seq[1]) > 1:
                return -1
            header = cmd_seq[ 1 ]
            self.default_cmd = self.sftp
            self.run_cmd( header )


        if len( cmd ) == 1:
            self.run_cmd( cmd )


        if cmd == "rtol":
            index= cmd_seq[ 1 ]
            item = self.sshrc.get_item( ord(index) - 97 )
            print "Local <-- Remote"
            home =  os.environ[ "HOME" ]
            local_file = raw_input( "本地文件/目录[%s]:" % home )
            if local_file == "":
                local_file= home
            remote_file = raw_input( "远程文件/目录:" )
            cmd =  "sshpass -p '%s' scp -r -o StrictHostKeyChecking=no -P %s %s@%s:%s  %s "\
                % (item.password, item.port, item.root, item.ip, remote_file,
                        local_file)
            os.system( cmd )

        if cmd == "ltor":
            index= cmd_seq[ 1 ]
            item = self.sshrc.get_item( ord(index) - 97 )
            print "Local --> Remote"
            home =  os.environ[ "HOME" ]
            local_file = raw_input( "本地文件/目录[%s]:"  % home)
            if local_file == "":
                local_file= os.environ[ "HOME" ]

            remote_file = raw_input( "远程文件/目录:" )

            cmd =  "sshpass -p '%s' scp -r -o StrictHostKeyChecking=no -P %s %s  %s@%s:%s "\
                % (item.password, item.port, local_file ,item.root, item.ip, 
                        remote_file)
            os.system( cmd )

    def run_cmd( self, index ):
        item = self.sshrc.get_item( ord(index) - 97 )
        self.item = item
        self.default_cmd( )

    def ssh( self ):
        item = self.item
        #cmd = "sshpass -p '%s' scp -P %s /home/feng/.bashrc  %s@%s:./ "\
        #        % (item.password, item.port, item.root, item.ip)
        #print color.red(cmd)
        #os.system(cmd)
        env_default = os.environ[ 'HOME' ] + '/Dropbox/flocal.py'
        set_title='echo  -e "\e]2;%s\a"'  % item.ip
        os.system(set_title )

        cmd =  "sshpass -p '%s' scp -o StrictHostKeyChecking=no -P %s %s %s@%s:/dev/shm/"\
                % (item.password, item.port, env_default, item.root, item.ip)

        os.system(cmd)

        cmd =  "sshpass -p '%s' ssh -o StrictHostKeyChecking=no -p %s %s@%s "\
                % (item.password, item.port, item.root, item.ip)

        print "User:   %s" % color.blue( item.root )
        print "Addr:   %s" % color.blue( item.ip )
        print "Port:   %s" % color.blue( item.port )
        os.system(cmd)

    def sftp( self ):
        item = self.item
        cmd =  "sshpass -p '%s' sftp  -P %s %s@%s "\
                % (item.password, item.port, item.root, item.ip)
        print color.red(cmd)
        os.system(cmd)


        





if __name__ == "__main__":
    sshm=_sshm( )
    sshm.sshrc.show_remote( )
    sshm.select( )

#        regex_param = r"^\[(\w+)\s+(.+)\]"
#        match = re.search(regex_ip, vim.current.line)
#        if  match:
#            param["ip"] =  match.group(1)
#        else:
#            return 1
#        line_nu = vim.current.window.cursor[0]
#        for line in vim.current.buffer[0: line_nu]:
#            match = re.search(regex_param, line)
#            if match:
#                param[match.group(1)] = match.group(2)
#    
#    
#        command = "xterm -e 'sshpass -p %s ssh -v  %s@%s -p %s'"  % (param["Password"], 
#                param["Root"], 
#                param["ip"], 
#                param["Port"])
#        os.popen2(command)
#        vim.command("quit")
#

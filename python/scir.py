#encoding:utf8
import subprocess
import time
import os
import ConfigParser
import stat
import paramiko
import tarfile
import StringIO
import fcntl
import ssh2
import termcolor
import yaml
from flushfile import flushfile

import sys
class log( object ):
    def __init__( self, logfile ):
        self.level = 4
        self.level_info = 4
        self.level_debug = 5

        self.logfile = logfile
        self.fd = open( logfile, 'w')
        self.saveout = sys.stdout
        self.saveerr = sys.stderr

        #sys.stdout = flushfile(self.fd)
        #sys.stderr = flushfile(self.fd)
    def reload( self ):
        self.fd.close( )
        self.fd = open( self.logfile, 'w')


    def write( self, msg ):
        self.fd.write( msg )
        self.fd.flush( )

    def info( self, msg ):
        if self.level >= self.level_info:
            self.write( msg )
    def debug( self, msg):
        if self.level >= self.level_info:
            self.write( msg )
color = termcolor.termcolor( )

yaml_temp= """
compile: 
   host: 192.168.33.83
   ssh_port: 22
   ssh_user: dingxuefeng
   ssh_password: dingxuefeng

install: 
   host: 192.168.33.155
   ssh_port:  30000
   ssh_user: root
   ssh_password: 123456!@#$%^

common: 
   log_tmp:  /tmp/SCIR_LOG
   compile_make_res: /tmp/compile

projects:
   - path: path-to-src
     timestamp: 0
"""

class Conf( object ):
    def __init__( self ):
        pass

    def read_conf( self, config_file ):
        self.config_file = config_file
        if os.path.isfile( self.config_file ):
            self.cf = yaml.load(open( self.config_file ))
        else:
            self.cf = self.create_cfg( )

        self.c_host= self.cf[ 'compile' ][ 'host' ]
        self.c_ssh_port=self.cf[ 'compile' ][ 'ssh_port' ]
        self.c_ssh_user=self.cf[ 'compile' ][ 'ssh_user' ]
        self.c_password=self.cf[ 'compile' ][ 'ssh_password' ]

        self.i_host=self.cf[ 'install' ][ 'host' ]
        self.i_ssh_port=self.cf[ 'install' ][ 'ssh_port' ]
        self.i_ssh_user=self.cf[ 'install' ][ 'ssh_user' ]
        self.i_password=self.cf[ 'install' ][ 'ssh_password' ]



        self.res_out = self.cf[ 'common' ][ 'compile_make_res' ]
        self.stdout_tmp = self.cf['common' ][ 'log_tmp' ] 

    def local_conf( self, root , bin_path):
        self.l_root_dir= root
        self.set_project( root )
        self.bin_path =  bin_path
    def compile_conf( self, root, make):

        self.c_root_dir= root
        self.c_cmd=make
    def install_conf( self, root='/tmp'):
        self.i_root_dir=root


    def section( self, name):
        for item in self.cf:
            if name in item.keys( ):
                return item.get( name )

    def set_project( self, path ):
        self.l_root_dir = path
        item = self.cf.get( 'projects' )
        for p in item:
            if p[ 'path' ] == self.l_root_dir:
                return 0
        item.append( {'path':path, 'timestamp':0} )


    def timestamp( self, timestamp=None ):
        item = self.cf.get( 'projects' )
        for p in item:
            if p[ 'path' ] == self.l_root_dir:
                break
        if timestamp:
            p[ 'timestamp' ] = timestamp
        return p[ 'timestamp' ]


        cf.write( open(self.config_file, 'w') )

    def create_cfg( self ):
        fileobj =  StringIO.StringIO( )
        fileobj.write( yaml_temp )
        fileobj.seek( 0)

        return yaml.load( fileobj)
    def close( self ):
        yaml.dump( self.cf, stream = open(self.config_file, 'w'), default_flow_style=False)



class Gui_stdout( ):
    def __init__( self, stdout ):
        self.stdout_tmp = stdout
    def open( self ):
        self.tail = subprocess.Popen(
                ['xterm' , '-e', 'tail -f %s' % self.stdout_tmp],\
                stdin=None,\
                stderr=subprocess.PIPE,\
                stdout=None)
    def close( self ):
        time.sleep( 5 )
        #conf.stdout.close( )

        self.tail.kill( )


class Src_files( object ):
    def __init__( self, timestamp, path ):
        if isinstance( timestamp, str ):
            self.timestamp = int(timestamp.split('.')[0])
        else:
            self.timestamp = timestamp

        self.path = path
        if path.endswith( '/' ):
            self.length = len( path )
        else:
            self.length = len( path ) + 1


    def filter( self, name , root):
        """
            过滤文件.
        """
     
        if name.endswith( '.ncb' ) or\
                name.endswith( '.sln' ) or\
                name.endswith( '.suo' ) or\
                name.endswith( '.vcproj' ) or\
                name.startswith( '.' ) or\
                name.endswith( '.o' ) or\
                name.endswith( '.lib' ):
            return False

        if name in [ 'Makefile.in', 'tags', 'vipro']:
            return False
        if os.stat( os.path.join(root, name))[ stat.ST_MTIME ]\
                < self.timestamp:
                    return False

        return True
    def scan( self ):
        src_files=[  ]
        for root, subdirs, files in os.walk( self.path ):
            for f in files:
                if not self.filter( f, root ):
                    continue
                src_files.append( os.path.join(
                    root[ self.length:], f)
                    )
        return src_files

class SCIR( object ):
    def __init__( self, stdout = sys.stdout ):
        self.conf = Conf( )

        #用于标准输出
        self.stdout = stdout
        
        self.client_c = None
        self.client_i = None

        self.cp = "tar jxm"
        self.loging=None

    def init_conf( self, conffile ):
        self.conf.read_conf( conffile )

        self.loging = log( self.conf.stdout_tmp )
        self.loging.info( 
            "<<<>>>>>>>>>>>>SCIR( sync, compile, install, run) Initting.<<<<<<<<<<<<>>>\n")

        self.gui_stdout = Gui_stdout( self.conf.stdout_tmp  )
    def reopen( self ):
        self.loging.reload( )

    def ssh_c_open( self ):
        if self.client_c:
            return 0
        conf = self.conf

        #conf = self.conf
        #client = paramiko.SSHClient()
        #client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        #client.connect(  )
        cir_ssh = ssh2.ssh2()
        cir_ssh.connect(  conf.c_host, conf.c_ssh_user,conf.c_password
                ,port=conf.c_ssh_port)
        self.client_c = cir_ssh.open_session( )



    def ssh_i_open( self ):
        if self.client_i:
            return 0

        conf = self.conf
        cir_ssh = ssh2.ssh2()
        cir_ssh.connect(  conf.i_host, conf.i_ssh_user,conf.i_password
                ,port=conf.i_ssh_port)
        self.client_i = cir_ssh.open_session( )

        #client = paramiko.SSHClient()
        #client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        #client.connect( conf.i_host, port=conf.i_ssh_port,
        #        username=conf.i_ssh_user, password=conf.i_password )

        #self.client_i = client

        """
            cmd
        """
    def ssh_i( self, cmd, in_msg=None, log_auto = False):
        self.ssh_i_open( )

        cmd = "cd %s;" % self.conf.i_root_dir + cmd
        return self.ssh( self.client_i, cmd, in_msg, log_auto)

    def ssh_c( self, cmd, in_msg=None, log_auto = False):
        self.ssh_c_open( )

        cmd = "mkdir -p {c_root};cd {c_root};" + cmd
        return self.ssh( self.client_c, cmd, in_msg, log_auto)

    def ssh( self, ssh_client, cmd, in_msg, log_auto):
        """
           stding_fg: 文件句柄. 作为输入
           cmd:  执行命令. 会通过 format 进行格式化.
                  root:  远程
           log_auto:  如果为True, 返回命令的 输出
        """
        conf = self.conf
        cmd = cmd.format(c_root=conf.c_root_dir, in_msg= in_msg)

        chan = ssh_client.open_chan( )
        chan.execute( cmd, out_merge = True)
        if in_msg != None:
            "发送数据"
            stdin = chan.stdin( )


            #此处 ssh4py 有bug. 如果数据大于缓冲区时, 不会续传余下的
            left = len( in_msg )
            length = left
            while( left > 0 ):
                n_send = stdin.write( in_msg[ length - left :]   )
                left = left -  n_send
            stdin.close( )

        if log_auto:
            stdout = chan.stdout( )
            while not chan.poll():
    
                info = stdout.read( 1024 )
                self.loging.info( info )
        else:
            return chan



    
    def build( self, cmd = None ):
        if cmd == None:
            cmd = self.conf.c_cmd
        make_dir = self.conf.c_root_dir
        if make_dir.startswith( '/' ):
            pass
        else:
            make_dir = "/home/%s/%s" %( self.conf.c_ssh_user, make_dir)

        self.loging.info( "<<<Compiling Start...>>>\n" )
        self.loging.info( cmd + '\n' )

        stdout_msg = "Build Now...."
        self.stdout.write( stdout_msg )

        stdout_msg = "Cmd: %s" % cmd
        self.stdout.write( stdout_msg )

        chan = self.ssh_c( cmd )
        
        "make 编译信息保存"
        stdout = chan.stdout( )
            

        while not chan.poll() :

            line = stdout.read( 1024 )
    
            if line == None or line == '' :
                break
            line = line.replace( make_dir , self.conf.l_root_dir)

            "输出到 日志"
            self.loging.info( line )
    
        self.loging.info( 
            "\n<<<Compile End.>>>\n") 

        self.stdout.write( "Build end." )

    
        #"写入到 res_out /tmp/compile "
        #open( self.conf.res_out, 'w' ).write(''.join(lines))
    
    def sync( self ):

        "过滤出要的文件"
        conf = self.conf
        src_files= Src_files( conf.timestamp(), conf.l_root_dir).scan( )
        if len( src_files )==0:
            
            self.loging.info(  "<<<No files to sync.>>>\n"  )
            return -1
        "输出到 统一 输出 会同步的文件"

        out_msg = "\n<<<Sync files[%s]:>>>\n" % len(src_files)
        self.loging.info( out_msg )
        self.loging.debug( '\n'.join(src_files) )
        self.stdout.write( out_msg )


        "切换到工作目录"
        os.chdir( conf.l_root_dir )

        "生成 tar bz2 文件"
        mem_tar = StringIO.StringIO( )
        tar = tarfile.open( fileobj=mem_tar, mode='w:bz2' )
        for f in src_files:
            tar.add( f )
        tar.close( )

        
        mem_tar.seek( 0 )


        self.ssh_c( self.cp, mem_tar.read( ) , log_auto =True )
        mem_tar.close( )

        self.conf.timestamp( time.time() )
        self.conf.close( )

        self.loging.info( 
            "\n<<<Sync over.>>> \n" )
        self.stdout.write( "<<<Sync over.>>>" )


    def install( self ):
        conf = self.conf 
        if conf.bin_path == '':
            conf.bin_path = '.'

        bin_name = os.path.basename( conf.bin_path )
        bin_path = conf.bin_path

        cmd = "cat %s" % bin_path 

        self.loging.info( cmd )
        chan = self.ssh_c(  cmd )

        stdout = chan.stdout( )

        file_bin = [  ]
        while not chan.poll():
            file_bin.append( stdout.read(  1024 ) )

        file_bin = ''.join( file_bin )



        rand_flag = time.strftime( "%d-%H-%M-%S" )
        rand_bin_name = "%s-SCIR-%s" % ( bin_name, rand_flag)

        self.ssh_i( "cat > %s"  %( rand_bin_name),in_msg
                = file_bin, log_auto=True)
        

    def run( self , bin_name):
        "bin_name 是在调试服务器上的执行程序的名字, 一般是随机的"
        pass








if __name__ == "__main__":
    conf = Conf( )
    conf.read_conf( )
    conf.local_conf( root= '/home/src/telnet', bin_name='telnetserver')
    conf.compile_conf( root= '/home/dingxuefeng/telnet', make="cd {c_root};./build.sh" )
    conf.install_conf( root='/root')
    
    
    A=SCIR( conf )
    A.sync(  )
    A.build( )
    conf.close( )
#build( )







#!/bin/env python2
#encoding:utf8
import os
import sys
import subprocess
import scir
import yaml
import argparse
import input_complete
import  termcolor
#from gi.repository import Gtk, GObject
#2014年 01月 04日 星期六 13:15:22 UTC
#   对于projectr 的数据管理方面进行了重构. 把project 进行了分析.
#   使结构更加合理.

#   增加了命令行的启动方式. 并暂时去掉了ui
#2013年 12月 15日 星期日 10:38:57 UTC
#   增加头文件跳转功能
"""
class PInfoWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Project Info")
        self.set_keep_above( True)      #置顶
        self.set_size_request(400, 300) #大小

        self.timeout_id = None
        

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        table = Gtk.Table( 12, 6, True)

        #Entry
        project_name_label = Gtk.Label("工程名称:")
        self.project_name      = Gtk.Entry()

        project_root_label = Gtk.Label("工程目录:")
        self.project_root      = Gtk.Entry()

        project_lang_label = Gtk.Label( "开发语言:" )
        self.project_lang      = Gtk.Entry(  )

        self.project_bin       = Gtk.Entry(  )
        self.compile_root      = Gtk.Entry(  )
        compile_build_cmd_label = Gtk.Label( "编译命令:" )
        self.compile_build_cmd = Gtk.Entry(  )
        self.install_root      = Gtk.Entry(  )

        table.attach( project_name_label      , 0, 1, 1, 2  )
        table.attach( self.project_name      , 1, 5, 1, 2  )

        table.attach( project_root_label      , 0, 1, 2, 3  )
        table.attach( self.project_root      , 1, 5, 2, 3  )
        #/table.attach( self.project_src       , 1, 5, 3, 4  )


        table.attach( project_lang_label      , 0, 1, 4, 5  )
        table.attach( self.project_lang      , 1, 5, 4, 5  )

        table.attach( self.project_bin       , 1, 5, 5, 6  )
        table.attach( self.compile_root      , 1, 5, 6, 7  )


        table.attach( compile_build_cmd_label , 0, 1, 7, 8  )
        table.attach( self.compile_build_cmd , 1, 5, 7, 8  )
        table.attach( self.install_root      , 1, 5, 8, 9 )

        self.add( table )

"""



class stdout( object ):
    def write( self, msg ):
        print( msg )
try:
    from pyvim import stdin
except:
    class stdin( object ):
        def read( self, msg ):
            return raw_input( msg )

class Projects( object ):
    def __init__( self ):
        """
            一般情况下,我们要管理多个工程或库.
            这工程有时会成为另一个工程的库.简单的说这些工程之间是有相互
            关联的,有必要进行统一的管理.


            管理多个工程(库)的方法是通过工程配置文件的方式.
            在工程的管理中,每一个工程的根目录下有一个配置文件,
            这个配置文件记录了工程的一些相关的信息.

            而对于这些工程进行管理的方法是通过链接的方式, 本模块会对于
            指定的目录进行查找, 这些目录下是这些要进行管理的工程的配置
            文件的链接

        """

        home = os.environ[ "HOME" ]
        dirs = os.path.join(home, '.mescin')
        self.projects = [ ]
        self.scan_dir( dirs )
    def scan_dir( self, dirname ):
        files = os.listdir( dirname )
        for f in files:
            ff =  os.path.join(dirname, f) 
            if os.path.islink( ff ):
                ff = os.path.relpath( ff )
            if os.path.isfile( ff ):
                try:
                    cfg = Project( cfgfile =  ff )
                    self.projects.append( cfg )
                except:
                    pass

    def show( self ):
        index = 1
        for name in self.get_names( ):
            if index % 2 == 1:
                print("%s :%s" %( index, termcolor.purple(name) ))
            else:
                print("%s :%s" %( index, termcolor.blue(name) ))
            index += 1

    def find_by_name( self, name ):
        for cfg in self.projects:
            if cfg.attr( 'project', "name") == name:
                return cfg
        return None

    def find_by_dir( self, dirname ):
        if os.path.isfile(dirname):
            dirname = os.path.dirname( dirname )

        if not os.path.isdir( dirname ):
            return -1

        for cfg in self.projects:
            dir_pro =  cfg.attr( 'path', 'src' )
            if  dir_pro == dirname:
                return cfg
        return None


    def get_info_for_select( self ):
        info = [  ]
        for cf in self.projects:
            name = cf.attr('project', 'name')
            root =  cf.attr( 'project', 'src' )
            info.append( ("%s (%s)" % (name, root), name, None, None)   )
        return info
    def get_names( self ):
        names = [  ]
        for cf in self.projects:
            names.append( cf.attr('project', 'name'))
        return names
    def select( self, arg ):
        "通过编号或是名字进行选择"
        if arg.isdigit( ):
            try:
                name = self.get_names( )[ int(arg) - 1 ]
            except IndexError:
                return None
        else:
            name = argv[ 2 ]
        return self.find_by_name( name )
    def open( self, name):
        cfg=self.select( name )
        if cfg:
            cfg.open( )
        

class Project( object ):
    def __init__( self, project_dir =None, cfgfile=None ):
        self.stdout  = stdout( )
        self.stdin = stdin( )
        self.cfgfile = cfgfile
        self.templete={ 
                'compile':{ 'root':      '',  'build_cmd':       "       "   },
                'install':{ 'root':      '',  },
                'project':{  'lang':      'c', 
                    'name':'', 
                    'src': '', 
                    'bin': '', 
                    'root':'' },
                'runtime':{ 'last_open': '',  'taglist':         0       },
                }
        if cfgfile == None:
            #创建一个空的cfg 对象
            self.cf = self.templete
        else:
            #根据cfg 文件创建
            self.cf = yaml.load( open(cfgfile) )
        if project_dir == None:
            home = os.environ[ "HOME" ]
            dirs = os.path.join(home, '.mescin')
            self.project_dir = dirs 
        else:
            self.project_dir = project_dir

    def load( self, cfgfile ):
        """
        载入或重新载入
        """
        self.cf = yaml.load( open(cfgfile) )

    def attr( self, section, attr  ):
        try:
            return self.cf[ section ][ attr ]
        except:
            return ""

    def set( self, section, attr , value ):
        self.cf[ section ][ attr ] = value
    def open( self):
        name = self.attr( 'project', 'name')
        
        subprocess.Popen( ["gvim", "-c","Project open %s" % name])

#    def write( self ):
#        path = self.attr( 'common', 'path')
#        path  = os.path.join(path, 'vipro' )
#        yaml.dump( self.cf, open(path, 'w'), default_flow_style=False)
    def create( self ):
        self.stdout.write("====Project====")
        while True:
            value = self.cf[ "project" ][ "name" ]
            res = self.stdin.read( "工程名称[%s]:" % value )
            if len( res ) ==  0 and len(value) == 0:
                continue
            self.cf[ "project" ][ "name" ]= res
            break
        self.stdout.write("")

        while True:
            value = self.cf[ "project" ][ "root" ]
            if value == '':
                value = os.path.realpath('.')
            res = self.stdin.read( "工程目录[%s]:" % value )
            if len( res ) == 0:
                res = value
            res = os.path.realpath( res )
            if os.path.isdir( res ):
                self.cf[ "project" ][ "root" ]= res
                break
        self.stdout.write("工程目录: [%s]\n" % res)

        os.chdir( res )
        while True:
            value = self.cf[ "project" ][ "src" ]
            res = self.stdin.read( "源码目录[%s]:" % value )
            if not res.startswith( '/' ):
                res = os.path.join(
                        self.cf[ "project" ][ "root" ], res)
            if os.path.isdir( res ):
                self.cf[ "project" ][ "src" ]= res
                break
        self.stdout.write("源码目录: [%s]\n" % res)


        while True:
            value = self.cf[ "project" ][ "bin" ]
            res = self.stdin.read( "目标文件[%s]:" % value )
            self.cf[ "project" ][ "bin" ]= res
            break
        self.stdout.write("目录文件: [%s]\n" % res)

        while True:
            value = self.cf[ "project" ][ "lang" ]
            res = self.stdin.read( "程序语言[%s]:" % value )
            if len( res ) ==  0:
                res = 'c'
            self.cf[ "project" ][ "lang" ]= res
            break
        self.stdout.write("程序语言: [%s]\n" % res)

        
        self.stdout.write("\n====远程编译服务器====")
        while True:
            value = self.cf[ "compile" ][ "root" ]
            if value == '':
                value = os.path.basename( self.cf['project']['root'] )
            res = self.stdin.read( "编译目录[%s]:"  % value)
            if len( res ) ==  0:
                res = value 
            self.cf[ "compile" ][ "root" ]= res
            break
        self.stdout.write("")

        while True:
            res = self.stdin.read( "编译命令:" )
            if len( res ) ==  0:
                res = "./build.sh"

            self.cf[ "compile" ][ "build_cmd" ] = res
            break

        self.stdout.write("\n====安装调试服务器====")
        while True:
            value = '/root'
            res = self.stdin.read( "安装目录[%s]:" % value )
            if len( res )  == 0:
                res = value
            self.cf[ "install" ][ "root" ] = res
            break
        self.submit( write=True )

    def submit( self, write=False ):
        self.print_info( )
        res = self.stdin.read( "submit: ")

        if len( res ) == 0 or res.startswith( 'y' ):
            if write:
                self.close( )
            return True

        if res == "write":
            self.close( )
            return True

        if res.startswith( 'n') or res.startswith( 'N'):
            return False

        return self.modify( )
    def close( self ):
        if self.cfgfile  == None:
            path_t = os.path.join( self.project_dir, 
                    self.cf[ 'project' ][ 'name' ])
            path = path_t
            id_= 1
            while  os.path.isfile( path ) or os.path.isdir( path ):
                path="%s(%s)" %(path_t , id_ )
                id_ += 1
            self.cfgfile = path

        f =  open( self.cfgfile, 'w')
        yaml.dump( self.cf, stream = f, default_flow_style=False )
        f.close( )

    def modify( self ):
        #TODO
        self.submit( )
        pass
    def print_info( self ):
        msgs = [  ]
        msgs.append("===========工程信息============")
        msgs.append("工程名称: [%s]" % self.cf[ 'project' ][ 'name' ] )

        msgs.append("工程目录: [%s]" % self.cf[ 'project' ][ 'root' ])
        msgs.append("源码目录: [%s]" % self.cf[ 'project' ][ 'src' ])

        msgs.append("程序语言: [%s]" % self.cf[ 'project' ][ 'lang' ])
        msgs.append("目录文件: [%s]" % self.cf[ 'project' ][ 'bin' ])

        msgs.append("编译目录: [%s]" % self.cf[ 'compile' ][ 'root' ])
        msgs.append("编译目录: [%s]" % self.cf[ 'compile' ][ 'build_cmd' ])

        msgs.append("安装目录: [%s]" % self.cf[ 'install' ][ 'root' ])
        Max = 0
        for m in msgs:
            Max = max(Max, len(m))
        self.stdout.write( '\n'.join(msgs) )

def mutual( projects ):
    while( True ):
        projects.show()
        cmd = raw_input( "输入命令与序列:" )
        if cmd.isdigit( ):
            projects.open( cmd )
            break
        if cmd == "create":
            p = Project( )
            p.create( )
        if cmd == "quit" or  cmd =="exit":
            break


        

def main( ):

    projects = Projects(  )
    argv = sys.argv
    if len( argv ) == 1:
        mutual( projects )
        return 0

    if argv[ 1 ] == 'create':
        A=Project()
        A.create( )
        return 0

    if len( argv ) < 3:
        return 0

    if argv[ 1 ] == 'open':
        name = argv[ 2 ]
        cfg = projects.open( name)


   



    


if __name__ == "__main__":

    input_complete.input_path( )
    main( )

    #win = PInfoWindow()
    #
    #win.connect("delete-event", Gtk.main_quit)
    #win.show_all()
    #Gtk.main()

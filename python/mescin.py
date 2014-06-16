#!/bin/env python2
#encoding:utf8
import os
import sys
import subprocess
import scir
import argparse
import input_complete
import  termcolor
import json
#from gi.repository import Gtk, GObject
#2014年 01月 04日 星期六 13:15:22 UTC
#   对于projectr 的数据管理方面进行了重构. 把project 进行了分析.
#   使结构更加合理.

#   增加了命令行的启动方式. 并暂时去掉了ui
#2013年 12月 15日 星期日 10:38:57 UTC
#   增加头文件跳转功能


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
                    cfg = Project( cfgfile =  ff )
                    self.projects.append( cfg )

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
            if not cfg.cf:
                continue
            t_name = cfg.get('name')
            if not name:
                t_name  = cfg.cf[ "project" ][0][ "name" ]
                if t_name == name :
                    return cfg
            else:
                if t_name == name :
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
            if not cf.cf:
                continue
            name = cf.get('name')
            if not name:
                name  = cf.cf[ "project" ][0][ "name" ]
                root  = cf.cf[ "project" ][0][ "src" ]
            else:
                root = cf.cf[ "project" ][ 0 ][ "path" ]
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
    key_project = "project"
    key_name = "name"
    key_path = "path"
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
            self.cf = None
            #根据cfg 文件创建
            try:
                s = open( cfgfile ).read( )
                cf = json.loads( s )
            except:
                cf = None
            if not cf:
                return
            if not cf.get( "project" ):
                return False
            self.cf = cf
            self.check( )
        if project_dir == None:
            home = os.environ[ "HOME" ]
            dirs = os.path.join(home, '.mescin')
            self.project_dir = dirs 
        else:
            self.project_dir = project_dir
    def check( self ):
        cf = self.cf
        if not cf:
            return False
        else:
            #检查project 是否是list
            if not isinstance( cf["project"], list):
                cf[ "project" ] = [ cf["project"] ]

            for p in cf[ self.key_project ]:
                if not p.get( self.key_path ):
                    del p
                if not p.get( self.key_name ):
                    p[ self.key_name ] = os.path.basename(p.get(self.key_path))
            #配置的name
            if not cf.get( self.key_name ):
                cf[ self.key_name ] = cf[ self.key_project ][ 0 ][ self.key_name ]

            self.cf = cf




    def get( self, key ):
        if not self.cf:
            return None
        return self.cf.get( key )
        

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
        f.write( json.dumps(self.cf ,sort_keys=True, indent = 4) )

        f.close( )

    def modify( self ):
        #TODO
        self.submit( )
        pass

    def print_info( self ):
        msgs = [  ]
        print self.cf[ 'project' ][0][ 'name' ]
        msgs.append("===========工程信息============")

        #msgs.append("工程目录: [%s]" % self.cf[ 'project' ][0][ 'root' ])
        #msgs.append("源码目录: [%s]" % self.cf[ 'project' ][0][ 'src' ])

        #msgs.append("程序语言: [%s]" % self.cf[ 'project' ][0][ 'lang' ])
        #msgs.append("目录文件: [%s]" % self.cf[ 'project' ][0][ 'bin' ])

        #msgs.append("编译目录: [%s]" % self.cf[ 'compile' ][ 'root' ])
        #msgs.append("编译目录: [%s]" % self.cf[ 'compile' ][ 'build_cmd' ])

        #msgs.append("安装目录: [%s]" % self.cf[ 'install' ][ 'root' ])
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


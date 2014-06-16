#encoding:utf8
import vim
import os
import sys
from pyvim import *
import pyvimrc
import pyvim
import scir
import mescin
import gatekeeper


#打开工程
class OprojectBase( object ):
    def __init__( self):
        #工程信息对象
        self.cfg = None  
        self.open_lock = False

    def open( self ):
        """
        依赖于 工程名打开工程
        """
        if self.cfg == None:
            return 0

        pyvimrc.Rootpath = self.cfg.attr( 'project','src' ).split( ',' )[ 0 ]
        self.on_open( )

    def name_cfg( self, name ):
        "通过工程名设定cfg"
        self.cfg = mescin.Projects( ).find_by_name( name )
        return self.cfg



    def on_open( self):
        if self.open_lock:
            return 2
        self.open_lock = True

        """只在第一次打开工程时运行.
            打开手册时不运行下面的代码
        """
        "打开上次关闭工程时打开着的文件"
        cfg = self.cfg
        last_opens = cfg.attr('runtime', 'last_open' )
        if last_opens != '':
            last_opens=last_opens.split(',')
            file_name= last_opens.pop( )
            try:
                vim.command( 'e %s' % file_name)
                if len( last_opens) > 0:
                    for file_name in last_opens:
                        vim.command( 'sp %s' % file_name)
            except:
                pass

        """taglist 如果上次打开,就再次打开"""
        if cfg.attr( 'runtime',  'taglist' ) == 1:
            w = vim.current.window
            vim.command( 'Tlist' )
            vim.current.window = w
        import frain_libs.data
        projects = self.cfg.get("project")
        for project in projects:
            frain_libs.data.append_path( project["path"], project["name"] )

        vim.command( "PathsExp "   )





        try:
            vim_title=self.cfg.attr('project', 'name').replace( ' ', '\\ ')
            vim.command( "set title titlestring=%s" % vim_title )
            #vim.command( "set lines=99999")
            #vim.command( "set columns=99999")
        except:
            pass


    def on_close( self):
        if not self.open_lock:
            return 0

        cfg = self.cfg

        files=[  ]
        for w in vim.windows:
            if w.buffer.options[ 'buftype' ] == '':
                files.append( w.buffer.name )
        files=','.join( files )

        try:
            cfg.set( 'runtime', 'last_open', files)
        except:
            pass
        



        self.cfg.close( )

class Oproject( OprojectBase ):
    def open_env( self ):
        return

    def open_name( self, name ):
        if self.name_cfg( name ) == None:
            return 
        self.open( )

class CompDebug( Oproject ):
    def __init__( self ):
        Oproject.__init__( self )
        self.comp_debug = None
        self.comp_debug_confirm = False

    def create_scir( self ):
        if not self.comp_debug_confirm:
            if self.cfg.submit( ):
                self.comp_debug_confirm  = True
            else:
                return 
                
        comp_debug = scir.SCIR( pyvim.stdout()  )
        comp_debug.init_conf( pyvimrc.comp_debug_conf )

        comp_debug.conf.local_conf( 
                root= self.cfg.cf['project'][0]['path'], 
                bin_path = ""
                )
        comp_debug.conf.compile_conf( 
                root= self.cfg.attr('compile', 'root'), 
                make= self.cfg.attr( 'compile', 'build_cmd' )
                )
        comp_debug.conf.install_conf( 
                root= self.cfg.attr( 'install', 'root' )
                )

        return comp_debug
    def build( self ):
        pyvim.log.info( "build" )

        comp_debug = self.create_scir( )
        if comp_debug == None:
            return 0
        
        comp_debug.sync( )
        #comp_debug.build( )

        #pyvim.quickfix_read_error( comp_debug.conf.stdout_tmp )
        #pyvim.quickfix( )
        

    def run( self ):
        return
        pyvim.log.info( "run" )
        comp_debug = self.create_scir( )
        comp_debug.install( )

        pyvim.quickfix_read_error( comp_debug.conf.stdout_tmp )
        pyvim.quickfix( )


    def cfgreload( self ):
        pass




VimProject = CompDebug( )

gatekeeper.register( "projects", mescin.Projects().get_info_for_select)


def manage( param='' ):
    if param == '':
        
        gate = gatekeeper.gatekeeper()
        gate.request( "/project/select/projects")

        project = gate.response( )

        if project.status() == 200:
            data = project.get_data( )
            if data:
                VimProject.open_name( data[1] )

        return 


    params = param.split( )
    if params[ 0 ] == 'create':
        projects.add( params[1], params[2] )
        
    if params[ 0 ] == 'open':
        if len( params ) > 1:
            VimProject.open_name( params[1] )
    if params[ 0 ] == 'env_open':
        VimProject.env_open( )

    if params[ 0 ] == 'favorite':
        VimProject.favorite( )

    if params[ 0 ] == 'set':
        if len( params ) > 2:
            VimProject.attr( params[1], params[2] )

    if params[ 0 ] == 'A':
        goto_include( )

    if params[ 0 ] == 'build':
        VimProject.build( )

    if params[ 0 ] == 'run':
        VimProject.run( )

    if params[ 0 ] == 'cfgreload':
        VimProject.cfgreload( )

def complete( A, L, P):
    L = L.lower( )
    cmdline = L.split( )
    params_1 = [ 'open', 'favorite', 'set', 'A' ]
    if len( cmdline ) == 1:
        return  params_1


    if len( cmdline ) == 2:
        if L.endswith( ' ' ):
            if cmdline[ 1 ] == 'open':
                return projects.get_names( )
        else:
            tmp = [  ]
            for p in params_1:
                if p.startswith( cmdline[1] ):
                    tmp.append( p )
            return tmp

    if len( cmdline ) == 3:
        if cmdline[ 1 ] == 'open':
            if L.endswith( ' ' ):
                    return projects.get_names( )
            else:
                tmp = [  ]
                for p in projects.get_names( ):
                    p_lower = p.lower( )
                    if p.startswith( cmdline[2] ):
                        tmp.append( p )
                return tmp

    return [  ]




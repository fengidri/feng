#encoding:utf8
import vim
import os
import sys
import pyvimrc
import pyvim
import scir
import gatekeeper

import frain_libs.mescin
import frain_libs.data


class project( object ):
    """
        处理同种的打开, 同步, 关闭
    """
    def __init__( self, cfg, runtime ):
        # 锁: 工程是否打开
        self.open_lock = False

        # 用户配置信息对象
        self.cfg = None

        # 运行状态对象
        self.runtime = None

    ############################################################################
    # 打开
    ############################################################################
    def on_open( self):
        if self.open_lock:
            raise "The project opened!"
        self.open_lock = True

        self._open_set_name( )
        self._open_last_opens( )
        self._open_path_exp( )



    def _open_last_opens( self ):
        last_opens=self.runtime.last_opens.split(',')
        if not last_opens:
            return
        file_name= last_opens.pop( )
        try:
            vim.command( 'e %s' % file_name)
            if len( last_opens ) > 0:
                for file_name in last_opens:
                    vim.command( 'sp %s' % file_name)
        except:
            pass

    def _open_path_exp( self ):
        cfg = self.cfg
        for project in cfg.src_path:
            frain_libs.data.append_path( project.path, project.name )
        vim.command( "PathsExp "   )
        vim.command( "wincmd p")

    def _open_set_name( self ):
        try:
            vim_title=self.cfg.name.replace( ' ', '\\ ')
            vim.command( "set title titlestring=%s" % vim_title )
        except:
            pass


    ############################################################################
    # 关闭
    ############################################################################
    def on_close( self):
        if not self.open_lock:
            return 0

        runtime = self.runtime
        files=[  ]
        for w in vim.windows:
            if w.buffer.options[ 'buftype' ] == '':
                files.append( w.buffer.name )
        files=','.join( files )

        runtime.last_opens = files

        runtime.save( )

    ############################################################################
    # 同步
    ############################################################################
    def sync( self ):
        pass



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


#encoding:utf8
import vim
import os
import time

import frain_libs.data
import frain_libs.scir
class cfg_api( object ):
    def clean_sync_time( self ):
        self.runtime.sync_time = 0


class project( cfg_api ):
    """
        处理同种的打开, 同步, 关闭
    """
    def __init__( self, cfg, runtime ):
        # 锁: 工程是否打开
        self.open_lock = False

        # 用户配置信息对象
        self.cfg = cfg

        # 运行状态对象
        self.runtime = runtime
        self.open( )

    ############################################################################
    # 打开
    ############################################################################
    def open( self):
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
        scir = frain_libs.scir.SCIR( )
        scir.c_connect( "192.168.72.205", "feng", "idri" )

        for project in self.cfg.src_path:
            path = project.path
            if not project.compile_info.path:
                remote_path = "sync/%s" % self.cfg.name
            else:
                remote_path = project.compile_info.path
            remote_path = os.path.join( remote_path, project.name )
            remote_path = remote_path.replace( " ", "\\ " )
            
            scir.sync( self.runtime.sync_time, path, remote_path )
        self.runtime.sync_time = time.time( )

    def sync_all( self ):
        """
            把所有的文件重新sync 一次
        """

        self.clean_sync_time( )
        self.sync( )

Project = None
def init( cfg, runtime ):
    global Project
    if Project:
        return
    Project=project( cfg, runtime )

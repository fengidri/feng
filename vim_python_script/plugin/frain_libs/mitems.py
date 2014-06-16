#encoding:utf8
import vim
import pyvim
from data import settings
from data import all_items_info

import paths_exp
import show_buffer_pos
import os
import mescin
import flog


def get_all_path( ):
    """
        返回所有的目录:
            返回当前的工程中的所有的目录
    """
    paths = [  ]
    paths_infos = settings.get( "paths" )
    if paths_infos:
        for path_info in paths_infos:
            path = path_info.get( "path" )
            if path:
                paths.append( path )
    return paths





class GoInclude( object ):
    def run(self ):
        #this is for c lang
        #goto the include file
        types = { 'c':['h'], 'h':['c', 'cpp'], 'cpp':['h'] }
        target_types = [  ]

        match = re.search('#include\s+["<](.+)[>"]', pyvim.getline( ))
        if match:
            target_files = [match.group( 1 )]
        else:
            target_files = [  ]
            base_name = os.path.basename( vim.current.buffer.name )
            model_name = base_name.split( '.' )[ 0 ]
            model_type = base_name.split( '.' )[ 1 ]
            target_types = types[ model_type ]
            for t in target_types:
                target_files.append( model_name + '.' + t )

        paths = settings.get( "paths" )
        if not paths:
            return -1
        for path in paths:
            path = path
        if pyvimrc.Rootpath in [ '', '/', os.environ['HOME'] ]:
            return -1
        for root, dirs, files in os.walk( pyvimrc.Rootpath ):
            for target_file in target_files:
                if target_file in files:
                    target_path = os.path.join( root, target_file )
                    pyvim.gotofile( target_path )
                    return 0
        pyvim.log.info( 'not find the file:%s'% target_file )
        
def frain_open(  ):
    """
        打开frain 模式:
              在设置好settings 的前提下打开frain 模式
    """
    paths_exp.refresh_nodes( )
    paths_exp.refresh_win( )




################################
# Commands API
################################


    """
        打开工程选择器. 选择工程并打开
    """
def frain_open_sel(  ):
    global settings
    names = get_all_name( )

    request = gui_options.request( "/gui/project_select" )
    request.add( "projects", names)

    con = gui_options.connect( )
    con.request( request )
    project = con.response( )
    con.close( )

    if project.status() == 200:
        name = project.get( "project_name" )[ 1 ]

        settings = mescin.get_info_by_name( name )
        frain_open(  )
    else:
        print project.status( )
    return 

    """
        1. frain 已经打开的情况下, 新加一个目录
        2. frain 没有打开的情况下, 打开一个目录, 进入frain 模式
    """
def frain_open_dir( dir_name ):
    if os.path.isdir( dir_name ):
        dir_name = os.path.realpath( dir_name )
        paths = settings[ "paths" ]

        paths.append( { "path": dir_name } )
        flog.loginfo( "%s" % settings)
        frain_open( )


def close( ):
    """
        退出frain 模式
    """
    global settings

    files=[  ]
    for w in vim.windows:
        if w.buffer.options[ 'buftype' ] == '':
            files.append( w.buffer.name )
    files=','.join( files )

    settings[ "last_open" ] = files

    """
        保存当前的数据信息到文件
    """
    mescin.save( settings )


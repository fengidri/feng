import frain_libs.data
import vim
import pyvim
import re
import os
class GotoInc( pyvim.command ):
    def run( self ):
        goto_include( )

def goto_include( ):
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


    paths = frain_libs.data.get_path( )
    cur_paths = vim.current.buffer.name
    project_path = None
    for path in paths:
        if cur_paths.startswith( path ):
            project_path = path
    if not project_path:
        return -1

    for root, dirs, files in os.walk( project_path ):
        for target_file in target_files:
            if target_file in files:
                target_path = os.path.join( root, target_file )
                pyvim.gotofile( target_path )
                return 0
    pyvim.log.info( 'not find the file:%s'% target_file )

log_handle = open( "/tmp/vimlog", 'w' )
def loginfo( msg ):
    log_handle.write( msg + "\n" )
    log_handle.flush( )

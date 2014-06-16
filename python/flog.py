log_handle = open( "/tmp/vimlog", 'w' )
def loginfo( msg ):
    return 
    print msg
    log_handle.write( msg + u"\n" )
    log_handle.flush( )

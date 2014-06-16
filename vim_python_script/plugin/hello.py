import pyvim
import time
import threading
import vim
import os
class Hellovim( pyvim.command ):

    def run( self ):
        print( "hello" )


class StartVhc( pyvim.command ):
    def run( self ):
        os.popen2( "python2 ~/Dropbox/root/lib/python/vim_handle_center.py&")

class TimeOut( pyvim.command ):
    def run( self ):
        vim.command( 'call feedkeys("\<Right>", "n" )')
        threading.Thread( target =thred, args=()  )



def thred( ):

    vim.command( 'call feedkeys("\<Right>", "n" )')


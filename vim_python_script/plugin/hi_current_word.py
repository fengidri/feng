#encoding:utf8
"""
  高亮当前word
"""
import pyvim
import vim
class _input_post( ):
    def __init__( self ):
        self.lastword = ''
        self.match_id = ''
        vim.command( "hi CurrentWord gui=underline")
        vim.command( "syn keyword CurrentWord CurrentWord"   )
    def input_post( self ):
        self.hi_current_word( )

    def hi_current_word( self ):
        current = pyvim.current_word( from_vim=False )

        if current.isspace() or current == '':
            return -2
        if self.lastword == current:
            return -1
        self.lastword = current
        if self.match_id != "":
            try:
                vim.command( "call matchdelete(%s)" % self.match_id)
            except:
                pass
        self.match_id = vim.eval( "matchadd('CurrentWord', '\<%s\>')" % current)
input_post = _input_post( )
class HiCurrentWord( pyvim.events ):
    def on_CursorMovedI( self ):
        input_post.input_post(  )


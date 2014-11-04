#encoding:utf8
import pyvim
import vim
class ShowBufferPos( pyvim.events ):
    def on_BufEnter( self ):
        #print "========"
        show( )



def show( ):
    #在NERDTree窗口中找到当前文件的位置
    """显示出当前文件的位置.
    当前是在NERDTree 中显示"""
    if vim.current.buffer.name == '':
        return -1
    if vim.current.buffer.options[ 'buftype' ] != '':
        return -1
    if pyvim.is_empty( ):
        return -1

    w = vim.current.window
    vim.command("PathsExpFind")
    vim.current.window = w
    return 0

#encoding:utf8
import pyvim
import vim

#本模块用于context wiki 由context_wiki.vim引用
#依赖于context模块

import context
import vim
import os

wiki_path = '/home/feng/Dropbox/my_vimwiki_site/wiki/'
html_path = u'/home/feng/Dropbox/my_vimwiki_site/html/'


class Cwiki( pyvim.command ):
    def run( self ):
        vim.command("e %sindex.mkiv"  % wiki_path)
        #vim.command(ur"au BufWritePost      WikiSave " %
        #        ( )

class  WikiSave( pyvim.command ):
    def run( self ):
        save( )
class WikiSaveAuto( pyvim.events ):
    def on_BufWritePost(self):
        save()
    def setting(self):
        self.set_pat(self.on_BufWritePost, "%s*.mkiv,%s*.wiki" % (wiki_path,
            wiki_path) )




def save():
    full_file_name = vim.current.buffer.name
    if full_file_name.startswith(wiki_path):
        file_name= os.path.basename( full_file_name )
        full_html_name = html_path  +  file_name.split('.')[0].decode('utf8')  + u'.html'
        try:
            context.context2html(full_file_name, full_html_name)
        except Exception,e:
            print e
    else:
        print full_file_name















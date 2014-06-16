
#encoding:utf8

"""
    相对于search 而言在数据的结构上提供更多的信息
    传入的src_list 的元素要求成员是(display_name, key_word, value, more)

    display_name: 用于list 显示的信息
    key_word:     用于返回的关键词. 大多时候这个值与display 相同. 但有一些时间,
                    如果在key_word 之外告诉用户更多的信息时, 就用上了display_name
    value:        有时, 我们要的并不key_word, key_word 只是告诉用户的信息, 我们
                    可能要的是, 这个名字对应的值.
    more:         用于将来的信息的扩展


    返回值将会也是这样一个元组. 在 search 内会用到的只有 display_name, key_word. 
    value, more 这两个信息会一同返回而已
"""
from gi.repository import Gtk, GObject, Pango, Gdk, GObject
import fuzzy
import os
import time

class SearchWindow(Gtk.Window):

    def __init__(self, src_list, res_value, title="Quick Search", filter_patten=None):
        self.filter_patten = filter_patten
        Gtk.Window.__init__(self, title=title)
        self.set_keep_above( True)      #置顶
        self.set_size_request(500, 450) #大小
        self.list_current=[  ]
        #self.set_position( Gtk.Align.CENTER)

        self.timeout_id = None

        size = Gdk.Screen.get_default()
        width=size.get_width( )
        height= size.get_height( )
        win_width, win_height = self.get_size( )
        self.move( width/2 - win_width/2, 30)
        self.set_decorated( False )
        

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        table = Gtk.Table( 7, 1, True)

        #Entry
        self.entry = Gtk.Entry()
        self.entry.set_text("")

        desc = Pango.FontDescription('monaco 18')
        self.entry.modify_font( desc )
        self.entry.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("green"))


        #listtore
        self.liststore = Gtk.ListStore(str)

        # liststore 显示对象
        treeview = Gtk.TreeView(model=self.liststore)
        treeview.set_headers_visible( False )

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn(None, renderer_text, text=0)
        treeview.append_column(column_text)
        desc = Pango.FontDescription('monaco 11')
        treeview.modify_font( desc )

        #treeview.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#242529"))
        #treeview.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#ffffff"))

        # 选择对象
        self.sel = treeview.get_selection( )
        self.sel.set_mode( Gtk.SelectionMode.SINGLE )

        #滚动窗口
        scroll = Gtk.ScrolledWindow( )
        scroll.add( treeview )

        #event
        self.entry.connect( "changed", self.event_change)
        self.entry.connect( "activate", self.event_activate)

        #layout
        #self.add(vbox)
        #vbox.pack_start(self.entry, True, True, 0)
        #vbox.pack_start(treeview, True, True, 0)
        #scroll.add_with_viewport( treeview )

        self.add( table )
        table.attach( self.entry, 0, 1 , 0, 1)
        table.attach( scroll, 0, 1, 1, 7)

        #init
        self.last_patten = None #上一次进行过滤的模式, 用于加快过滤速度
        self.src_list = src_list
        self.res_value = res_value


        self.refresh_list( '' )

        self.activate_focus( )
        self.set_focus( self.entry )



    def event_change( self, event):
        patten = self.entry.get_text( )

        if  self.filter_patten:
            patten, src_list = self.filter_patten( patten )
            if src_list:
                self.src_list = src_list

        #默认是文件切换
        if patten.startswith( '@' ):#全局函数
            pass
        elif patten.startswith( '$' ):#全局tags
            pass

        #快速进行滚动选择
        if patten.find( " " ) > -1:
            try:
                index = patten.split( " " )[ -1 ]
                if index.startswith( 'q' ):#退出
                    self.destroy( )
                    Gtk.main_quit( )
                    return 

                if index.isdigit( ):
                    index = int( index ) - 1
                else:

                    index = index.count( 'j' ) - index.count( 'k' )
                list_iter = self.liststore.get_iter( index )
                self.sel.select_iter( list_iter )
            except:
                pass
            return 

        self.refresh_list( patten )

    def event_activate( self, event):
        list_mode, list_iter = self.sel.get_selected( )
        if list_iter == None:
            res = (None, None, None, None) 
        else:
            index = list_mode.get_path( list_iter ).get_indices( )[ 0 ]
            res = self.list_current[ index ]
        self.res_value.append( res )
        self.destroy( )
        Gtk.main_quit( )
        return 

    def refresh_list( self, patten ):
        self.liststore.clear( )
        del self.list_current[ : ]
        if patten:
            index = 0
            for item in self.src_list:
                if index > 25:
                    break
                if fuzzy.diffuse( patten, item[1] ):
                    index += 1
                    self.list_current.append( item )
                    if item[ 0 ]:
                        self.liststore.append( [item[0]] )
                    else:
                        self.liststore.append( [item[1]] )
        else:
            for item in self.src_list:
                self.list_current.append( item )

                if item[ 0 ]:
                    self.liststore.append( [item[0]] )
                else:
                    self.liststore.append( [item[1]] )

        list_iter = self.liststore.get_iter_first( )
        if list_iter:
            self.sel.select_iter( list_iter )

        


def timeout( cmd ):
    print "time out"
    os.system( cmd )

def search( src_list, filter_patten = None ):
    if src_list == None:
        src_list = [  ]
    res = [ None ]
    win = SearchWindow(src_list, res, filter_patten = filter_patten)
    cmd = "xdotool search --name '%s' windowfocus" %  win.get_title( )
    GObject.timeout_add(100, timeout,cmd)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    return res[ -1 ]


if __name__ == "__main__":
    src_list = [
[            "one","one","one","one"],
[            "two","two","two","two"],
[            "thr","thr","thr","thr"],
[            "moo","moo","moo","moo"],
[            "one","one","one","one"],
[            "two","two","two","two"],
[            "thr","thr","thr","thr"],
[            "moo","moo","moo","moo"],
[            "one","one","one","one"],
[            "two","two","two","two"],
[            "thr","thr","thr","thr"],
[            "moo","moo","moo","moo"],
[            "one","one","one","one"],
[            "two","two","two","two"],
[            "thr","thr","thr","thr"],
[            "moo","moo","moo","moo"],
[            "one","one","one","one"],
[            "two","two","two","two"],
[            "thr","thr","thr","thr"],
[            "moo","moo","moo","moo"],

            ]
    print search( src_list )

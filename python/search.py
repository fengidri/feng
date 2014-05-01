#encoding:utf8
from gi.repository import Gtk, GObject, Pango,  Gdk
import fuzzy
import time

class SearchWindow(Gtk.Window):

    def __init__(self, src_list, res_value, title="Quick Search"):
        Gtk.Window.__init__(self, title=title)
        self.set_keep_above( True)      #置顶
        self.set_size_request(500, 450) #大小
        #self.set_position( Gtk.Align.CENTER )
        size = Gdk.Screen.get_default()
        width=size.get_width( )
        height= size.get_height( )
        win_width, win_height = self.get_size( )
        self.move( width/2 - win_width/2, 30)
        self.set_decorated( False )


        self.timeout_id = None
        

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
        desc = Pango.FontDescription('monaco 14')
        treeview.modify_font( desc )
        treeview.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#242529"))
        treeview.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("#ffffff"))

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
        for item in self.src_list:
            self.liststore.append( [item] )

        self.activate_focus( )
        self.set_focus( self.entry )


    def event_change( self, event):
        patten = self.entry.get_text( )

        #快速进行滚动选择
        if patten.find( " " ) > -1:
            try:
                index = patten.split( " " )[ -1 ]
                if index.startswith( 'q' ):
                    #self.destroy( )
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

        self.liststore.clear( )
        index = 0
        if patten:
            for item in self.src_list:
                if index > 50:
                    break
                if fuzzy.diffuse( patten, item ):
                    index += 1
                    self.liststore.append( [item] )
        else:
            for item in self.src_list:
                self.liststore.append( [item] )

        list_iter = self.liststore.get_iter_first( )
        if list_iter:
            self.sel.select_iter( list_iter )
    def event_activate( self, event):
        list_mode, list_iter = self.sel.get_selected( )
        if list_iter == None:
            res = (None, None) 
        else:
            index = list_mode.get_path( list_iter ).get_indices( )[ 0 ]
            value = list_mode[ list_iter ][ 0 ]
            res = ( index, value)
        self.res_value.append( res )
        self.destroy( )
        Gtk.main_quit( )
        return 
        




def search( src_list ):
    res = [ (None, None) ]
    win = SearchWindow(src_list, res)
    
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    return res[ -1 ]



if __name__ == "__main__":

        src_list = [
                "<red>one</red>", "two", "thr", "moo",
                "one", "two", "thr", "moo",
                "one", "two", "thr", "moo",
                "one", "two", "thr", "moo",
                "one", "two", "thr", "moo",
                ]
        print search( src_list )

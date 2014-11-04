
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
from gi.repository import Gtk, GObject, Pango, Gdk, Wnck
import fuzzy
import socket
import vhc_protocol
import os
import re

def activate(window):
    screen = Wnck.Screen.get_default()
    screen.force_update()
    for win in screen.get_windows():
        if win.get_name( ) == "Quick Search":
            win.activate(int(time.time()))
            print "activate"
            return 



class Con( object ):
    def __init__( self ):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect( ("localhost", 9394) )
        self.buf = ""

    def register( self ):
        req = vhc_protocol.request( "/vhc/register/GoAnyUi" )
        self.sock.send( req.dump_data() )

    def waiting( self ):
        buf = self.buf
        while True:
            data = self.sock.recv( 1204 )
            buf = buf + data
            while True:
                get, buf = vhc_protocol.get_one_req_from_buf(  buf )
                if not get:
                    break
                if get.get_data( ) == vhc_protocol.Alive:
                    print "Alive"
                    continue
                else:
                    self.buf = buf 
                    return get

    def request( self, req):
        self.sock.send( req.dump_data() )
    def send_data( self, data ):
        res = vhc_protocol.response( vhc_protocol.Vim )
        print "Request:%s" % res.url( )
        res.set_data( data )
        self.sock.send( res.dump_data() )
    def close( self ):
        if self.sock:
            self.sock.close( )




        


class GoAnyUiWindow(Gtk.Window):
    """
        构造窗口, 设置事件的回调
    """

    def __init__(self, title="Quick Search"):
        
        Gtk.Window.__init__(self, title=title)
        self.set_keep_above( True)      #置顶
        self.set_size_request(500, 650) #大小
        #self.set_position( Gtk.Align.CENTER)

        self.timeout_id = None

        size = Gdk.Screen.get_default()
        width=size.get_width( )
        height= size.get_height( )
        win_width, win_height = self.get_size( )
        self.move( width/2 - win_width/2, 30)
        self.set_decorated( False )

        self.set_focus_on_map( True )
        self.set_accept_focus( True )
        

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



        self.activate_focus( )
        self.set_focus( self.entry )



    def event_change( self, event):
        pass

    def event_activate( self, event):
        pass
    def get_sel_context( self ):
        #TODO
        list_mode, list_iter = self.sel.get_selected( )
        if list_iter == None:
            return None
        else:
            #index = list_mode.get_path( list_iter ).get_indices( )[ 0 ]
            return list_mode.get_value( list_iter , 0)
    def get_sel_index( self ):
        list_mode, list_iter = self.sel.get_selected( )
        if list_iter == None:
            return -1
        else:
            index = list_mode.get_path( list_iter ).get_indices( )[ 0 ]



class GoAnyAnly( GoAnyUiWindow ):
    """
        数据的运算处理
    """
    def get_struct_by_sel( self ):
        context = self.get_sel_context( )
        if context:
            for res in self.src_list:
                if res[ 0 ] == context or res[1] == context:
                    return res
        res = (None, None, None, None) 


    def event_activate( self, event): #回车
        res = self.get_struct_by_sel( )

        self.send_data( res )

        Gtk.main_quit( )
        return 
    def event_change( self, event): #按键触发
        patten = self.entry.get_text( )
        tmp  = patten.split( " " )
        if len( tmp ) > 1:
            self.control( tmp[ 1 ] )
        elif len(tmp) == 1:
            patten = self.filter_patten( tmp[0] )
            self.refresh_list( patten )
        else:
            patten = ""
            self.refresh_list( patten )

    def control( self, index  ):
        try:
            if index.startswith( 'q' ):#退出
                res = (None, None, None, None) 
                self.send_data( res )

                Gtk.main_quit( )
                return


            elif index.isdigit( ):
                index = int( index ) - 1
            else:
                index = index.count( 'j' ) - index.count( 'k' )

            list_iter = self.liststore.get_iter( index )
            self.sel.select_iter( list_iter )
        except:
            pass
        return 
    def refresh_list( self, patten, max_nu = 25 ):
        self.liststore.clear( )
        items = []
        index = 0
        if patten:
            for item in self.src_list:
                if index > max_nu:
                    break
                res = fuzzy.diffuse( patten, item[1] )
                if res > -1:
                    index += 1
                    if item[ 0 ]:
                        items.append( (res, [item[0]]) )
                    else:
                        items.append( (res, [item[1]]) )
            items = sorted(items, key = lambda x:x[0])
        else:
            for item in self.src_list:
                if index > max_nu:
                    break
                index += 1
                if item[ 0 ]:
                    items.append( (0, [item[0]]) )
                else:
                    items.append( (0, [item[1]]) )

        for item in items:
            self.liststore.append( item[1] )

        list_iter = self.liststore.get_iter_first( )
        if list_iter:
            self.sel.select_iter( list_iter )

    def filter_patten( self, patten ):
        """
            对于已经输入的内容进行解析
        """
        pass
    def send_data( self, data):
        pass


class GoAny( GoAnyAnly ):
    """
        业务层面的解析
    """
    def __init__( self ):
        GoAnyAnly.__init__( self )
        self.con = Con( )
        self.con.register( )
        self.current_target = "init"  # file, file_fun, file_vars, init
        self.info ={  }
        #self.info_file_fun = None              # @
        #self.info_file_vars = None             # #
        self.file_path = ""
        self.current_file =""
        self.switch_target( )
            
        self.refresh_list( '' )
    def switch_target( self ):
        src_list = self.info.get( 
                "%s_%s" %(self.file_path, self.current_target)
                )
        if src_list:
            self.src_list = src_list
        else:
            url = "/Vim/GoAnyUi/%s" % (self.current_target )
            req = vhc_protocol.request( url )
            req.set_data( self.file_path )

            self.con.request( req )
            res = self.con.waiting( )

            self.src_list = self.info[
                "%s_%s" %(self.file_path, self.current_target)
                    ] = res.get_data( )

            cur_file  = res.get_by_key( "current_file" )
            if cur_file:
                self.current_file = cur_file

            cur_target  = res.get_by_key( "current_target" )
            if cur_target:
                print cur_target
                self.current_target = cur_target



        return

    def send_data( self, data ):
        #对于数据进行过滤, go any 只要有文件名和行号就可以了
        file_path =None
        line_nu  = None
        print self.current_target
        if self.current_target == "file":
            file_path = data[ 2 ]
        else:
            file_path = self.file_path
            line_nu = data[ 2 ]

        self.con.send_data(  (file_path, line_nu) )

    def filter_patten( self, patten ):
        print patten
        pos = -1
        flag = 0
        pos = patten.find( "@" ) #函数
        if patten  == "@":

            file_path = self.current_file
            self.current_target= "file_fun"
            patten = ""
            flag = 1

        elif patten == "#":
            file_path = self.get_struct_by_sel()[2]
            self.current_target= "file_vars"
            patten = ""
            flag = 1
            
        elif patten.endswith("@"):
            file_path = self.get_struct_by_sel()[2]
            self.current_target= "file_fun"
            patten = ""
            flag = 1

        elif patten.endswith( "#" ):
            file_path = self.get_struct_by_sel()[2]
            self.current_target= "file_vars"
            patten = ""
            flag = 1

        elif patten.find( "@" ) > -1:
            patten = patten.split( "@" )[ 1 ]
            flag = 0

        elif patten.find("#") > -1:
            patten = patten.split( "#" )[ 1 ]
            flag = 0

        #else:
        #    if self.current_target != "file":
        #        self.current_target  = "file"
        #    file_path = ""
        #    flag = 1

        if flag == 1 and file_path:
            self.file_path = file_path
            self.switch_target( )
        return patten





#def timeout( cmd ):
#    print "time out"
#    os.system( cmd )
        
        






if __name__ == "__main__":
    win = GoAny( )
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    #cmd = "xdotool search --name '%s' windowfocus" %  win.get_title( )
    #GObject.timeout_add(2000, timeout,cmd)
    Gtk.main( )


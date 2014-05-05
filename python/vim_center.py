#encoding:utf8
"""
 vim_handle_center.
 这是一个vim 的辅助进程. 在系统中单独运行. 与vim 之间通过网络进行通信.
 其功能是提供一些图形化的交互.在将来也可能会发展成为一个功能更加全面的
 进程.

功能说明
     1. 可以解决vim python 中的多线程的问题.

     2. 通过vim  直接调用wx 在close 时会出现 vim 窗口也同时close 的情况.
     猜测是由于wx 与gvim 都是使用的gtk 实现的问题. 同时使用gvim 调用一些
     图形接口可能有一些别的问题出现. 

     3. 远程的问题. 之前有一个问题在于通过putty 这样的程序进行远程使用vim 时,
     不可以调用图形接口. 但是使用这种分离式的方式可以完全解决这个问题.

     4. 这个模块在实现上不中人是实现gui 的操作, 它是作为一个事件处理中心存在的.
        可以调用更多的工具进行事件处理.

通信协议
    有想过使用http(nginx). 但是http 的短连接不能合符要求. 
    所以使用socket 直接实现服务器.



"""
'''
Created on 2012-1-6
The poll function provides similar features to select() , but the underlying implementation is more efficient.
But poll() is not supported under windows .
@author: xiaojay
'''
import socket
import select 
import Queue
import wx_notify
from vhc_protocol import request, response
import search
import info_search
import os
READ_ONLY = ( select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
READ_WRITE = (READ_ONLY|select.POLLOUT)


vim_gui_proc = "/home/feng/Dropbox/root/lib/python/vim_center.py"
vim_center_ip = "127.0.0.1"
vim_center_port =  9394

 
class vhc( object ):
    def __init__( self, local_ip="127.0.0.1", local_port=9394 ):

        # Create a TCP/IP socket, and then bind and listen
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (local_ip, local_port)
         
        print  "Starting up on %s port %s" % server_address
        server.bind(server_address)
        server.listen(5)
        self.server = server

        self.message_queues = {}
        #The timeout value is represented in milliseconds, instead of seconds.
        self.timeout = 1000
        self.cons = {  }

    def deal( self, s):
        print "========================:"
        req = request( )
        buf = [  ]
        s = self.sock
        while True:
            data = s.recv(1024)
            buf.append( data )
            if len(data) != 1024:
                data = ''.join( buf )
                break
        if not data:
            # Stop listening for input on the connection
            self.poller.unregister(s)
            s.close()
            return 
            #del message_queues[s]
        try:
            req.init_by_json( data )
        except:
            res.set_status( 404, "json error" )
            res.send( s )
            return 
        self.deal_req( req )

    def run( self ):
        # Set up the poller
        poller = select.poll()
        poller.register(self.server, READ_ONLY)
        self.poller = poller

        #Map file descriptors to socket objects
        fd_to_socket = {self.server.fileno():  self.server,}
        while True:
            events = poller.poll( self.timeout)
            for fd ,flag in  events:
                s = fd_to_socket[fd]
                if flag & (select.POLLIN | select.POLLPRI) :
                    if s is self.server :
                        # A readable socket is ready to accept a connection
                        connection , client_address = s.accept()
                        print "Connection " , client_address
                        connection.setblocking(False)
                         
                        fd_to_socket[connection.fileno()] = connection
                        poller.register(connection,READ_ONLY)
                        self.cons[ connection ] = Con( connection, poller )
                    else:
                        self.deal( s )

                elif flag & select.POLLHUP :
                    #A client that "hang up" , to be closed.
                    print "Closing ", s.getpeername() ,"(HUP)"
                    poller.unregister(s)
                    s.close()
                elif flag & select.POLLOUT :
                    #Socket is ready to send data , if there is any to send
                    try:
                        next_msg = self.message_queues[s].get_nowait()
                    except Queue.Empty:
                        # No messages waiting so stop checking
                        print s.getpeername() , " queue empty"
                        poller.modify(s,READ_ONLY)
                    else :
                        print " sending %s to %s" % (next_msg , s.getpeername())
                        s.send(next_msg)
                elif flag & select.POLLERR:
                    #Any events with POLLERR cause the server to close the socket
                    print "  exception on" , s.getpeername()
                    poller.unregister(s)
                    s.close()
                    del self.message_queues[s]



class Con:
    def send( self, msg ):
        self.sock.send( msg )



class Con_vim(Con):
    def __init__( self, sock ):
        self.sock = sock
        self.fsm_file=""
        self.fsm_search = ""
        self.poller = poller
        self.remote_gui = ""
        self.queue_vim = [   ]

    def reg_gui(self, con_gui ):
        self.remote_gui = con_gui
        for req in self.vim_queue:
            self.remote_gui.send( req.data )
    def unreg_gui(self):
        self.remote_gui = None

    def request( self, request , param = None):
        """
           param 是传递给数据回调的参数 
        """
        request_obj = request( request )
        request_obj.add( "param", param)

        self.sock.send( request_obj.dump_data() )


    def filter_patten( self, patten ):
        if patten.startswith( "@" ):#当前文件中的变量, 函数
            if self.fsm_search == "local_var_fun":
                return patten[ 1: ], None
            else:
                self.fsm_search = "local_var_fun"
                return patten

        if patten.startswith( "$" ):#全局的变量函数
            pass

    def start_gui( self ):
        
        os.popen2( "python2 %s %s %s %s", vim_gui_proc, vim_center_ip,
                vim_center_port, self.sock.fileno() )

    def deal_req( self, req ):
        res = response( )

        print req.url( )
        #数据转发给gui
        if req.url( ).startwith( "/gui/" ):
            if self.remote_gui:
                self.remote_gui.send( req.data )
            else:
                #启动gui
                self.start_gui( )
                #把数据放到队列中去
                self.queue_vim.append( req )

        #gui 注册,
        if req.url( ).startwith( "/vim_center/register/gui" ):


        if req.url().startswith("/gui/notify"):
            notify = req.get( "notify" )
            wx_notify.notify( notify )
            self.send( res.dump_data() )
            return 

        if req.url().startswith("/gui/project_select"):
            project_name  = info_search.search( req.get_data() )
            res.add_data(  project_name)
            self.send( res.dump_data() )
            return 

        if req.url().startswith("/gui/tag_jump"):
            tags = req.get( "tags" )
            tag  = search.search( tags )
            if tag[ -1 ] == None:
                res.set_status( 404, "Tag Not Found" )
            else:
                res.set( "tag", tag)
            self.send( res.dump_data() )
            return 

        if req.url().startswith("/gui/localjump"):
            pos  = info_search.search( req.get_data() )
            if pos :
                res.add_data( pos)
            else:
                res.set_status( 404, "Pos Not Found" )
            self.send( res.dump_data() )
            return 
        if req.url().startswith("/gui/switch_file"):
            selected  = info_search.search( req.get_data() )
            if selected :
                res.add_data( selected )
            else:
                res.set_status( 404, "Not Found" )
            self.send( res.dump_data() )
            return 


        res.set_status( 404, "Not Found" )
        res.send( s )






if __name__ == "__main__":
    vhc( ).run( )
















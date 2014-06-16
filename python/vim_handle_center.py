
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
#import wx_notify
from vhc_protocol import request, response, notify
import vhc_protocol
#import search
import info_search
import os
import time
READ_ONLY = ( select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
READ_WRITE = (READ_ONLY|select.POLLOUT)
Vim_Half = None
Gui_Half = None
class _half(  ):
    def __init__( self ):
        self.who = "" # vim,GoAnyUi,project
        self.buf = ""
        self.sock =None

    def send( self, trans ):
        print "=======>%s" % self.who
        self.sock.send( trans.dump_data() )

    def alive( self ):
        
        nt = notify( self.who )
        nt.set_data( vhc_protocol.Alive )
        self.sock.send( nt.dump_data() )

        


 
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
        self.buf = ""
    def keepalive( self , last_point):
        global Vim_Half
        global Gui_Half
        cur_time = time.time( )
        if cur_time - last_point < 1:
            return last_point
            

        if Vim_Half:
            try:
                Vim_Half.alive( )
            except:
                Vim_Half = None

        if Gui_Half:
            try:
                Gui_Half.alive( )
            except:
                #对于VIM 发出结束包的 TODO
                Gui_Half = None
        return cur_time


    def run( self ):
        # Set up the poller
        poller = select.poll()
        poller.register(self.server, READ_ONLY)
        self.poller = poller

        #Map file descriptors to socket objects
        fd_to_socket = {self.server.fileno():  self.server,}
        time_point = time.time( )
        while True:

            events = poller.poll( self.timeout )
            time_point = self.keepalive( time_point )

            for fd ,flag in  events:
                sock = fd_to_socket[fd]
                if flag & (select.POLLIN | select.POLLPRI) :
                    if sock is self.server :
                        # A readable socket is ready to accept a connection
                        sock_con , client_address = sock.accept()
                        print "sock_con " , client_address
                        sock_con.setblocking(False)
                         
                        fd_to_socket[sock_con.fileno()] = sock_con
                        poller.register(sock_con,READ_ONLY)
                    else:
                        self.deal( sock )

                elif flag & select.POLLHUP :
                    #A client that "hang up" , to be closed.
                    print "Closing ", s.getpeername() ,"(HUP)"
                    poller.unregister(sock)
                    sock.close()
                elif flag & select.POLLOUT :
                    #Socket is ready to send data , if there is any to send
                    try:
                        next_msg = self.message_queues[sock].get_nowait()
                    except Queue.Empty:
                        # No messages waiting so stop checking
                        poller.modify(sock,READ_ONLY)
                    else :
                        sock.send(next_msg)
                elif flag & select.POLLERR:
                    #Any events with POLLERR cause the server to close the socket
                    print "  exception on" , s.getpeername()
                    poller.unregister(sock)
                    sock.close()
    def deal( self, sock):
        buf = [ self.buf  ]

        try:
            data = sock.recv(1024)
        except:

            print "Close"
            self.poller.unregister(sock)
            sock.close()
            return 

        if not data:

            self.poller.unregister(sock)
            sock.close()
            return 

        buf.append( data )
        if len( data ) == 1024:
            while True:
                try:
                    data = sock.recv(1024)
                except:
                    break
                buf.append( data )
                if len(data) != 1024:
                    break

        print "Recv Data"
        data = ''.join( buf )
        while True:
            req, data = vhc_protocol.get_one_req_from_buf(  data )

            if req:
                self.deal_trans_data( req , sock)
            else:
                break
        
        self.buf = data


    def deal_trans_data( self, trans_data ,sock):
        global Vim_Half
        global Gui_Half
        print trans_data.url( )
        url = trans_data.url( )

        #if trans_data.url().startswith("/gui/notify"):
        #    notify = trans_data.get( "notify" )
        #    wx_notify.notify( notify )
        #    self.send( res.dump_data() )
        #    return 

        if url.startswith("/project/select"):
            res = response( "Vim" )
            project_name  = info_search.search( trans_data.get_data() )
            res.set_data(  project_name )
            sock.send( res.dump_data() )
            return 
        else:


            if url.startswith( "/GoAnyUi/start" ):
                os.popen2( "python2 /home/feng/Dropbox/root/lib/python/GoAnyUi.py > /tmp/goany" )
                pass

            elif url.startswith( "/GoAnyUi" ):
                if Gui_Half and Gui_Half.who == vhc_protocol.GoAnyUi:
                    Gui_Half.send(  trans_data )

            elif url.startswith( "/Vim" ):
                if Vim_Half and Vim_Half.who == vhc_protocol.Vim:
                    Vim_Half.send(  trans_data )

            elif url.startswith( "/vhc/register/GoAnyUi" ):
                Gui_Half = _half( )
                Gui_Half.who = vhc_protocol.GoAnyUi
                Gui_Half.sock = sock

            elif url.startswith( "/vhc/register/Vim" ):
                Vim_Half = _half( )
                Vim_Half.who = vhc_protocol.Vim
                Vim_Half.sock = sock









if __name__ == "__main__":
    vhc( ).run( )
















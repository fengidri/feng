#encoding:utf8
import urllib
import pyvim
import json
import socket
import vhc_protocol
import os
import time
import flog
import select
vhc_addr = ("localhost", 9394)

g_requests = {}

"""
    这个模块用于与vim center 进行通信.
    与vim center 之间是vhc_protocol. 通过对于数据包的解析完成.
    同时这个模块也处理与vim 这一侧的数据交互.
    之所以起gate keeper 这个名字就是因为这个模块就如同门房一样的.

    对外是数据, 对内的数据是通过房间号一样的方法进行处理. 通过回调得到数据
"""

def register(  data_name, callback, param=None ):
    """
        注册数据回调
    """
    g_requests[ data_name ] = (callback, param)

class Gate_con( object ):
    """
        完成对于重连机制的封装
    """
    def __init__( self ):
        self.sock = None
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect( vhc_addr )
        self.sock.setblocking( False )


    def send( self, msg ):
        sock =  self.sock
        sock.send( msg )


    def close( self ):
        self.sock.close( )

class Gate_mag( object ):
    """
        对于业务进行管理: 注册, 提取数据
    """
    
    
    def get_data( self, data_name, param = None ):
        """
            返回info search 的数据结构
        """
        res = [  ]
        callback = g_requests.get( data_name )

        if callback:
            if param:
                res = callback[0]( param )
            else:
                res = callback[0](  )
        return res


class gatekeeper( Gate_con, Gate_mag ):
    """
         对于连接层与管理层的封装以完成上层的业务请求
    """



    def response( self ):
        """
            进入等待响应状态. 
            在这个状态下, 等待数据返回. 但这个过程是双工的. 所以可能得到的不是返
            回的数据, 而是数据的请求.
        """
        buf = ""
        while True:
            readable , writable , exceptional =\
                    select.select([self.sock], [], [], 5)

            if not ( readable or writable or exceptional ):
                """ timeout """
                flog.loginfo( "TimeOut" )
                return vhc_protocol.response( vhc_protocol.Vim )

            data = self.sock.recv( 1204 )
            buf = buf + data
            while True:
                req_res, buf = vhc_protocol.get_one_req_from_buf( buf )
                if not req_res:
                    break
                if req_res.get_data( ) == vhc_protocol.Alive:
                    flog.loginfo( "Alive" )
                    continue
                else:
                    return req_res
        self.buf = buf 
        return req_res


    
    
    def request( self, url , param = None):
        """
           param 是传递给数据回调的参数 
        """
        data_name = url.split( '/' )[ -1 ]

        request_obj = vhc_protocol.request( url )
        context = self.get_data( data_name, param )
        request_obj.set_data( context )

        self.send( request_obj.dump_data() )
    def req_with_data( self, url, data=None ):
        res = vhc_protocol.response( url )
        res.set_data( data )

        self.send( res.dump_data() )

    def just_req( self, url ):
        flog.loginfo( "just req")
        request_obj = vhc_protocol.request( url )
        self.send( request_obj.dump_data() )
        flog.loginfo( "end")

    def reg_to_vhc( self ):
        req = vhc_protocol.request( "/vhc/register/Vim" )
        self.send( req.dump_data() )






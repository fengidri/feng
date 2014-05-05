#encoding:utf8
"""
    格式:
VHC json-data\r\n
length:%d\r\n
[json]
"""


"""

request:
    /register/GoAnyUi
    /register/Vim
    

"""
import json
import re
OK=0
TooShort=1
NotMatch=2
Vim="Vim"
GoAnyUi="GoAnyUi"
Alive="alive"
class res_req( object ):
    def __init__( self ):
        self.net_data = { 
                "request_line":"",
                "Title":"",
                "data":None
                    }




    def dump_data( self ):
        json_str  =  json.dumps( self.net_data )
        json_len = len( json_str )
        return "VHC json-data\r\nlength:%d\r\n%s" %( json_len, json_str )

    def load_data( self, data ):
        self.net_data = json.loads( data )

    def is_req( self ):
        if self.net_data[ "request_line" ].split()[0].isdigit( ):
            return False
        else:
            return True


    def init_by_json( self , res_json):
        self.net_data = json.loads( res_json )

    def request_line( self ):
        return self.net_data.get( "request_line" )




    def status( self ):

        return int( self.request_line().split()[0] )



    def get_data( self):
        return self.net_data.get( "data" )

    def set_data( self, data ):
        self.net_data[ "data" ] = data

    def set_request_line( self, req_line ):
        self.net_data[ "request_line" ] = req_line

    #def get_request_line( self ):
    #    return self.net_data[ "request_line" ]

    def url( self ):
        return self.net_data[ "request_line" ].split( )[ 1 ]

    def add_data( self, key, value ):
        """
            增加额外的key
        """
        self.net_data[ key ] = value
    def get_by_key( self , key):
        return self.net_data.get( key  )




# get /Vim/GoAnyUi/file
# 200 /Vim  OK
# notify /Vim
#

def response( Target, Status=200, Msg="OK", self="" ):
    res = res_req( )
    request_line = "%s /%s %s %s" %(Status,  Target, Msg, self )
    res.set_request_line( request_line )
    return  res

def request( url, self="" ):
    req = res_req(  )
    request_line= "get %s %s" % (url, self)
    req.set_request_line( request_line )
    return req

def notify( target ):
    notify = res_req( )
    request_line = "notify /%s" % target
    notify.set_request_line( request_line )
    return notify




def get_len( buf ):
    res = ( -1, -1, -1)

    if not buf:
        return (-1,"",0)
    start = -1
    
    len_start = -1
    len_end = -1

    pos = buf.find( "VHC json-data\r\n" )
    if pos == -1:
        return (-1,"",0)
    start = pos

    pos = buf.find( ":", pos)
    if pos == -1:
        return (-1,"", start)

    len_start = pos + 1
    pos = buf.find( "\r\n", pos)
    if pos == -1:
        return (-1,"", start)

    len_end = pos
    length= buf[ len_start:len_end ]
    if length.isdigit( ):
        length = int( length )

        if length < 0 :
            return (-1, "", start)
        else:
            return ( length , buf[pos +2:], start )




def get_one_req_from_buf( buf ):
    length, buf_left, start = get_len( buf )
    if start == -1:
        if len( buf ) > 20:
            return (None, buf[-20:])
        else:
            return (None, buf)
    else:
        if length > -1:
            if len( buf_left ) >= length:
                get = res_req( )
                get.load_data( buf_left[0:length] )
                return (get, buf_left[length:] )
        return (None, buf[ start: ])




















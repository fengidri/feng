#encoding:utf8
import json
class res_req( object ):

    def add_data(self, data):
        self.net_data[ "data" ] = data

    def get_data( self):
        return self.net_data.get( "data" )

    def dump_data( self ):
        return json.dumps( self.net_data )

class request( res_req ):
    def __init__( self, net_data="", title="" ):
        """
            net_data 字段的值如:/vhc/file_switch/files
              vhc: 是接收者
              file_switch: 是名称
              files: 是数据名称. 数据名如果房间号一样, 门房通过房间号提取出对应
              的数据.
        """
        self.net_data={ 
                "request":net_data,
                "Title":title,
                "data":None,
                
                }
    def add( self, key, value):
        self.net_data[ key ] = value

    def init_by_json( self , res_json):
        self.net_data = json.loads( res_json )

    def get( self, key ):
        return self.net_data.get( key )
    def url( self ):
        return self.net_data.get( "request" )


class response( res_req ):
    def __init__( self ):
        self.net_data = { "response": "200/OK" }

    def init_by_json( self , res_json):
        self.net_data = json.loads( res_json )

    def status( self ):
        res = self.net_data.get( "response")
        return int( res.split("/")[0] )

    def set_status( self, stat, msg ):
        self.net_data[ "net_data" ] = "%d/%s" %( stat, msg)

    def set( self, key, value):
        self.net_data[ key ] = value

    def get( self, key ):
        return self.net_data.get( key )

    def send( self, con):
        con.send( json.dumps(self.net_data) )


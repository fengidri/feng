#encoding: utf-8
import socket 
import libssh2   
import os



class ssh2( object ):
    def __init__( self  ):
        pass

    def connect( self, ip,  user_name, user_pwd, port= 22):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sock.connect(( ip, port))   
        
        session = libssh2.Session() 

        session.startup(sock) 
        session.userauth_password(user_name, user_pwd)
        self.session = session

    def open_session( self ):
        return Session( self.session )

class Session( object ):
    def __init__( self, session):
        self.__session = session
    def scp_recv( self, remote_path, local_path ):
        channel, (size, mode , mtime, atime) =  self.__session.scp_recv( remote_path, 1 )
        buf =  channel.read( size )
        f = open( local_path, 'w')
        f.write( buf )
    def scp_send( self, local_path, remote_path):
        st = os.stat( local_path )
        channel = self.__session.scp_send( remote_path, 0644, st.st_size)
        f = open( local_path )
        
        while True:
            buf = f.read( 1024 )
            channel.write( buf)
            if len( buf )  < 1024:
                break
        channel.send_eof( )
        channel.wait_eof( )
        return True
        #channel.dealloc( )

    def open_chan( self ):
        channel = self.__session.channel( )
        return Channel( channel )


class Channel( object ):
    def __init__( self, channel):
        self.__channel = channel

    def execute( self, cmd, out_merge=False ):
        if out_merge:
            cmd = "%s 2>&1" % cmd
        self.__channel.execute( cmd )

    def stdin( self ):
        return stdin_fileobj( self.__channel )

    def stdout( self ):
        return stdout_fileobj( self.__channel )

    def stderr( self ):
        return stdout_fileobj( self.__channel )

    def poll( self ):
        return self.__channel.eof
    def exit_status( self ):
        return self.__channel.get_exit_status( )


class stdin_fileobj( object ):
    def __init__( self , channel ):
        self.channel = channel
        self.closed = False

    def write( self, msg):
        if self.closed:
            return  -1
        return self.channel.write( msg)

    def flush( self ):
        self.channel.flush( )

    def close( self ):
        if not self.closed:
            self.closed = True
            self.flush( )
            self.channel.send_eof( )

class stdout_fileobj( object ):
    def __init__( self , channel ):
        self.channel = channel
        self.closed = False

    def read( self, length ):
        if self.closed:
            return 0
        return self.channel.read( length  )

    def flush( self ):
        self.channel.flush( )

    def close( self ):
        if not self.closed:
            self.closed = True
            self.flush( )
            self.channel.send_eof( )

if __name__ == "__main__":
    con = ssh2()
    con.connect( ip='192.168.33.83',user_name = 'dingxuefeng',\
            user_pwd='dingxuefeng' )
    session  = con.Session( )
    cmd = 'ping baidu.com 2>&1'
    channel = session.chan(  )
    
    channel.execute( cmd )
    
    stdin = channel.stdin( )
    stdout = channel.stdout( )
    
    while not channel.poll():
    
        data = stdout.read(1024)
        print 'strout'
        print data,
    

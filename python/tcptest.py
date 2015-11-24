# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-11-05 06:00:23
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

import select
import socket
import Queue
import time

def Server():
    #create a socket
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setblocking(False)
    #set option reused
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)

    server_address= ('127.0.0.1', 9090)
    server.bind(server_address)

    server.listen(10)

    #sockets from which we except to read
    inputs = [server]

    #sockets from which we expect to write
    outputs = []

    #Outgoing message queues (socket:Queue)
    message_queues = {}

    #A optional parameter for select is TIMEOUT
    timeout = 20

    while inputs:
        print "waiting for next event"
        readable , writable , exceptional = select.select(inputs, outputs, inputs, timeout)

        # When timeout reached , select return three empty lists
        if not (readable or writable or exceptional) :
            print "Time out ! "
            continue

        for s in readable :
            if s is server:
                # A "readable" socket is ready to accept a connection
                connection, client_address = s.accept()
                print "    connection from ", client_address
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = Queue.Queue()
            else:
                data = s.recv(1024)
                if data :
                    print " received " , data , "from ",s.getpeername()
                    message_queues[s].put(data)
                    # Add output channel for response
                    if s not in outputs:
                        outputs.append(s)
                else:
                    #Interpret empty result as closed connection
                    print "  closing", client_address
                    if s in outputs :
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    #remove message queue
                    del message_queues[s]


        for s in writable:
            #try:
            #    next_msg = message_queues[s].get_nowait()
            #except Queue.Empty:
            #    print " " , s.getpeername() , 'queue empty'
            #    outputs.remove(s)
            #else:
            #    print " sending " , next_msg , " to ", s.getpeername()
            #    s.send(next_msg)
            s.send("HTTP/1.1 200 OK\r\n")
            s.send("X-Source: CC\r\n")
            s.send("Content-Length: 1000\r\n")
            s.send("\r\n")
#            s.send("via\r\n")
            time.sleep(2)

            if s in outputs :
                outputs.remove(s)
            if s in inputs:
                inputs.remove(s)

            del message_queues[s]
            s.close()

        for s in exceptional:
            print " exception condition on ", s.getpeername()
            #stop listening for input on the connection
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            #Remove message queue
            del message_queues[s]

Server()


#import signal
#import socket
#import select
#def signal_handle():
#    s.close()
#
#signal.signal(signal.SIGINT, signal_handle)

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind(('127.0.0.1', 9090))
#s.settimeout(0.2)
#s.listen(5)
#
#while True:
#    s
#    con, addr = s.accept()
#    print "-------------"
#    while True:
#        buf = con.recv(1024)
#        if len(buf) < 1024:
#            break
#
#        if not buf:
#            break
#
#    print "#############"
#    con.send("HTTP/1.1 200 OK\r\n")
#    con.send("x_source: CC\r\n")
#    con.send("via\r\n")
#    con.close()
#s.close()


if __name__ == "__main__":
    pass



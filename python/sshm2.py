#! /bin/env  python2
#encoding:utf8
import string
import re
import os
import sys
from tree_ui import Tree, Leaf, Node
import termcolor

class Item:
    type_host = "host"
    type_section = "section"

    root='root'
    ip=''
    des=''
    port=22
    password=''
    type = "host" # host section
    section_name = ""

    @staticmethod
    def factory(line):
        if len(line) < 3:
            return 
        line = line.replace("\n", "")
        tmp = Item( )
        if line.startswith(">"):
            tmp.type = Item.type_section
            tmp.section_name = line
            tmp.des = line[1:]
        else:
            line_split = line.split( )
            if len(line_split) > 3:
    
                tmp.root=line_split[ 0 ]
                tmp.ip=line_split[ 1 ]
                tmp.port=int(line_split[ 2 ])
                tmp.password = line_split[ 3 ]
    
            if len(line_split) > 4:
                tmp.des=' '.join(line_split[ 4: ])
        return tmp
    def display(self):
        if self.type ==  Item.type_section:
            return self.des
        else:
            return "%s %s" % (self.ip.ljust(15), self.des)


class _sshrc:
    def __init__( self ):
        
        self.get_items(self.get_lines( ))
    def show_list(self, items):
        header = list_header()
        i = 0
        section = 0
        for item in items:
            i = i + 1 

            context = None
            if item.type == Item.type_section:
                context = header.next() + item.section_name
                section = 1
            else:
                if section:
                    continue
                context = header.next()+ item.ip.ljust(16)+ \
                        str(item.port).ljust(7)+ item.des

            if i%2  == 0:
                context = color.blue(context)
            else:
                context = color.red(context)
            print context

    def show_all_remote( self ):
        self.show_list(self.items)

    def show_section(self, section_name):
        self.show_list(self.get_items_of_section(section_name))

    def get_items_of_section(self, section_name):
        items = []
        flag = 0
        for item in self.items:
            if item.type == Item.type_section:
                if flag == 0:
                    flag = 1
                    continue
                if flag == 1:
                    break
            if flag != 1:
                continue
            items.append(item)
        return items



    def get_lines( self ):
        sshrc = os.path.join(os.environ[ "HOME" ], ".sshrc")
        f=open( sshrc )
        lines= f.readlines( )
        f.close( )
        return lines

    def get_items( self, lines ):

        items=[  ]

        for line in lines:
            tmp = Item.factory(line)
            if not tmp:
                continue
            items.append( tmp )

        self.items=items
        return items

    def get_item( self, index ):
        return self.items[ index ]

    def get_item_by_host( self, host):
        for item in self.items:
            if item.ip == host:
                return item
        return None



class _sshm( object ):
    def __init__( self ):
        self.sshrc= _sshrc( )
        self.tree = Tree()
        tree = self.tree
        for item in self.sshrc.items:
            if item.type == Item.type_section:
                node = Node(item.display())
                node.item = item
                tree.select_root()
                tree.append(node)
                tree.select_root(node)
            else:
                node = Leaf(item.display())
                node.item = item
                tree.append(node)
    def select(self):
        leaf = self.tree.select()
        if not leaf:
            return
        item = leaf.item
        session = Session(item.root, item.password, item.ip, item.port)
        session.session()





    def cmd_header( self, cmd ):
        cmd_seq= cmd.split( )
        cmd = cmd_seq[ 0 ]
        if cmd == "muti":
            indexs = raw_input(color.green("select host:"))
            index_list= indexs.split()
            prefix = color.green(",".join(index_list) + "$")
            session_list = []
            for index in index_list:
                session_list.append(self.get_session(index))

            while True:
                cmd = raw_input(prefix)
                if cmd == "quit" or cmd == "exit":
                    break
                for s in session_list:
                    print color.red("========%s========" % s.host)
                    s.cmd(cmd)
                print color.blue("===========================================")





        if len( cmd ) == 1:
            session = self.get_session(cmd)
            session.session()



    def get_session(self, index):
        if index.isupper( ):
            index = ord(index) - ord('A') + 26
        else:
            index = ord(index) - ord('a') 
        item = self.sshrc.get_item( index )
        session = Session(item.root, item.password, item.ip, item.port)
        return session
        


class Session(object):
    def __init__(self, user,pwd, host, port=22):
        self.host = host
        self.port = port
        self.password = pwd
        self.user = user
    def cmd(self, cmd):
        cmd =  "sshpass -p '{pwd}' ssh -o \
 StrictHostKeyChecking=no -p {port} {user}@{host} '{cmd}'".format(
         pwd = self.password,
         port = self.port,
         user = self.user,
         host = self.host,
         cmd = cmd
                )
        os.system(cmd)
    def session(self):
        env_default = os.environ[ 'HOME' ] + '/Dropbox/flocal.py'
        cmd =  "sshpass -p '%s' scp -o StrictHostKeyChecking=no -P %s %s %s@%s:/dev/shm/"\
                % (self.password, self.port, env_default, self.user, self.host)

        res = os.system(cmd)

        cmd =  "echo  -e '\e]2;{host}\a';sshpass -p '{pwd}' ssh  -o \
        StrictHostKeyChecking=no -p {port} {user}@{host} ".format(
                pwd = self.password,
                port = self.port,
                user = self.user,
                host = self.host,
                cmd = cmd
                )

        print "User:   %s" % termcolor.blue( self.user )
        print "Addr:   %s" % termcolor.blue( self.host )
        print "Port:   %s" % termcolor.blue( self.port )
        os.system(cmd)





        





def main():
    sshm=_sshm( )
    sshm.select( )


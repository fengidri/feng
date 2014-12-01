import termcolor
import string
import os
def list_header(  ):
        for letter in string.lowercase + string.uppercase:
            yield "%s." % (letter)
class Node(list):
    def __init__(self, name):
        self.name = name
        list.__init__(self)
    def display(self):
        return "+%s/" % self.name


class Leaf(object):
    def __init__(self,name):
        self.name = name
    def display(self):
        return self.name

class ExitEx(Exception):
    pass

class Tree(object):
    prefix_dir = "+"
    def __init__(self):
        self.__tree = Node("root")
        self.__cur_node = self.__tree

    def append(self, item):
        self.__cur_node.append(item)

    def select_root(self, node=None):
        if node == None:
            self.__cur_node = self.__tree
        else:
            self.__cur_node = node

    def show(self, root):
        if not isinstance(root, Node):
            return 
        
        os.system('clear')
        print "========%s============" % root.name
        lines = [item.display() for item in root]
        header = list_header()
        for i, line in enumerate(lines):
            context =  "%s %s" % (header.next(), line)
            if i%2  == 0:
                context = termcolor.blue(context)
            else:
                context = termcolor.red(context)
            print(context)
    def input(self, size):
        while True:
            index = raw_input("select one:")
            if index == "quit":
                return
            if index == "exit":
                raise ExitEx()
            if len(index) != 1:
                continue
            if index.isupper( ):
                index = ord(index) - ord('A') + 26
            else:
                index = ord(index) - ord('a') 
            if index >= size or index < 0:
                continue
            return index
    def select(self, root=None):
        try:
            return self._select(root)
        except ExitEx:
            pass
    def _select(self, root=None):
        if not root:
            root = self.__tree
        self.show(root)
        while True:
            index = self.input(len(root))
            if index == None:
                return 
            try:
                return self.get(root, index)
            except ExitEx:
                self.show(root)
                continue

    def get(self, root, index):
        item = root[index]
        if isinstance(item, Leaf):
            return item
        if not isinstance(item, Node):
            raise Exception("item[%s] not Leaf or Node" % Node)
        return self._select(item)





















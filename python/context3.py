# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-03-13 16:15:52
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
# 这是第五次写这个功能了吧!!!!


# TODO 不支持 $$
import codecs
import sys


# 1. 使用split 函数把source 分成多个Word对象, 所有的Word 实例组成Words 实例
# 2. 依赖于Words 中的Word.type 创建node. 这些node 组成node_tree

class LostParamsEx(Exception):
    def __init__(self, word):
        print "%s:%s Lost Param" % (word.pos[0], word.pos[1])


class Word( object ): 
    "词法对象"
    TEX_CHAR = ['%','#','$','&','{','}', '^', '_', '~', '[', ']', ' ', '\n']
    TEX_CONTROL_CHAR = ['#', '$', '%', '^', '&', '_', '{', '}', '~', '\\']


    TYPE_CONTROL = 1  # 控制序列
    TYPE_PUNC    = 2  # 特殊符号
    TYPE_TEXT    = 3  # 文字
    TYPE_CPUNC   = 4  # 形如\# \$ \% \^ \& \_ \{ \} \~ \\

    def __init__(self, t, l, name, pos):
        self.pos = pos 

        self.len = l   # 长度
        self.type = t   # 对应类型
        self.nm = name


    def name(self):
        return self.nm
           


class Source(object): # 对于souce 进行包装
    def __init__(self, source):
        self.pos = 0
        self.source = source
        self.length = len(source)

    def getchar(self): # 得到当前的char
        if self.pos >= self.length:
            return None
        return self.source[self.pos]

    def update(self): # 记数器+1
        self.pos += 1



class PostionCounter(object): # 计算当前的位置
    def __init__(self, source):
        self.line = 1
        self.col = 0
        self.source = source
        self.col_start = 0

    def update(self, char):
        if char == '\n':
            self.line += 1
            self.col_start = self.source.pos

    def get_pos(self):
        col = self.source.pos - self.col_start
        return (self.line, col, self.source.pos)


def get_control(source, pos):
    length = 1

    name = []
    name.append(source.getchar())

    source.update()
    tp = Word.TYPE_CPUNC

    while source.getchar():
        char = source.getchar()
        if length == 0:
            if char in Word.TEX_CONTROL_CHAR:
                length += 1
                name.append(char)
                source.update()
                tp = Word.TYPE_PUNC
                break
        elif char.islower():
            length+=1
            name.append(char)
            source.update()
            continue
        else:
            break
            # 序列结束
    name = ''.join(name)
    return Word(tp, length, name, pos)

             
class Words(list):# 对于进行词法分析的结果进行包装, 是语法分析中的依赖
    def __init__(self, source):
        list.__init__(self)
        self.pos = 0
        self.source = source # 记录source, 不是source 对象

    def getcontext(self, word): 
        # 依据word 的pos 与length 得到对应的source
        pos = word.pos[2]
        length = word.len
        return self.source[pos: pos + length]

    def get_context_between(self, w1, w2): # 得到两个word 中间的context, 开区间
        s = w1.pos[2] + w1.lenght
        e = w2.pos[2] 
        return self.source[s, e]

    def find_end_by_name(self, name):
        for index, w in enumerate(self[self.pos:]):
            if w.name() == name:
                self.pos = self.pos + index + 1
                return self[self.pos: index + 1]
        else:
            w = self[self.pos]
            msg = "NOT FOUND:%s from %s, %s" % (name, w.pos[0], w.pos[1])
            raise Exception(msg)

    def find_same(self, name):
        for index, w in enumerate(self[self.pos:]):
            if w.name() != name:
                self.pos = self.pos + index + 1
                return self[self.pos: index]
        else:
            return []

    def getword(self):
        if self.pos >= len(self):
            return None
        return self[self.pos]

    def update(self):
        self.pos += 1

    def back(self): # 使用要注意
        self.pos -= 1







def split(src): # 对于src 进行词法分解
    source = Source(src)
    poscounter = PostionCounter(source) # 统计当前的行号, 位置信息

    words = Words(src)
    text_pos = poscounter.get_pos()
    
    while True:
        char =  source.getchar()
        if not char : break
        # start

        if char in Word.TEX_CHAR or char == '\\':
            # 处理普通文本
            if text_pos:
                l = poscounter.get_pos()[2] - text_pos[2]
                w = Word(Word.TYPE_TEXT,  l, 'text', text_pos)
                words.append(w)
                text_pos = None

            if char in Word.TEX_CHAR:# 特殊字符

                w = Word(Word.TYPE_PUNC, 1, char, poscounter.get_pos())
                words.append(w)
                poscounter.update(char)  # 更新行
                source.update()


            elif char == '\\': # 控制序列
                w = get_control(source, poscounter.get_pos())
                words.append(w)

                
                # 处理结束的char 不是序列的, 再次进入循环
                continue
        else:
            if text_pos == None:
                text_pos = poscounter.get_pos()
            
            poscounter.update(char)  # 更新行
            source.update()
    return words

def show_word_details(words):
    for w in words:
        c = w.context()[0:20].strip()
        name = w.name()
        if w.type == Word.TYPE_PUNC:
            if name == '\n':
                name = '\\n'
            elif name == ' ':
                name = 'space'

        print "%s|%s,%s|%s" % (name, w.pos[0], w.pos[1], c)



################################################################################
# 完成词法分析, 下面的代码实现语法分析, 生成多个语法树
################################################################################
class node_text(object):
    def __init__(self, ws):
        self.word = ws.getword()
        self.context = ws.getcontext(self.word)

        ws.update()

    def html(self):
        return self.context

class node_cpunc(object): # 形如: \%
    def __init__(self, ws):
        self.word = ws.getword()
        self.context = ws.getcontext(self.word)[1:2]

        ws.update()
    def html(self):
        return self.context

class node_punc(object):
    def __init__(self, ws):
        self.word = ws.getword()
        word = self.word

        self.name =  self.word.name()

        if self.name == '%':
            ws.find_end_by_name('\n')
            self.h =  ''

        if self.name == ' ':
            ws.find_end_by_name(' ')
            self.h =  ' '

        elif self.name == '\n':
            if len(ws.find_same('\n')) > 1:
                self.h = '<br />\n'

            else:
                self.h = '\n'

        elif self.name == '$':
            #TODO
            ws.find_end_by_name('$')
            self.h = ''

        else:
            self.h = self.name

        ws.update()

    def html(self):
        return self.h

class node_control(object): 
    """
        1. 控制序列后面出现的{}, [], 一定会被处理掉
        2. 控制序列后面出现的\n, space 也会被处理掉
    """
    def __init__(self, ws):
        self.Params = []
        self.Attrs  = []

        list.__init__(self)
        self.word = ws.getword()
        self._getattrs()
        self._getparams()
        self.init(ws)

    def init(self, ws):
        ws.update()

    def html(self):
        return ''

    def _getparams(self, ws): # 得到参数, 参数可以有多个, {}
        while True:
            ws.update()
            word = ws.getword()

            name = word.name()
            if name in ['\n', ' ']:
                continue

            if name == '{':
                ps = ws.find_end_by_name('}')
                p = node_tree(ps[1:-1])
                self.Params.append(p)
            else:
                ws.back()
                break

    def _getattrs(self, ws): # 得到属性, 也可以有多个, []
        while True:
            ws.update()
            word = ws.getword()

            name = word.name()
            if name in ['\n', ' ']:
                continue

            if name == '[':
                ps = ws.find_end_by_name(']')
                p = node_tree(ps[1:-1])
                self.Attrs.append(p)
            else:
                ws.back()
                break

class Section( node_control ):
    def init(self, ws):
        ws.update()
        self.name = self.word.name()

    def html( self ):
        name = self.name
        level = name.count('sub') + 3

        if not self.Params:
            raise LostParamsEx(self.word)
        c = self.Params[0].html()

        h = "\n\n<h%s>%s</h%s>\n" % (level, c, level)
        return h
        


class Typing( node_control ):
    def init(self, ws):
        tps = ws.find_end_by_name("\stoptyping")

        self.context = ws.get_context_between(tps[0], tps[-1])

    def html( self ):
        tp = self.context

        tp = tp.replace('&', "&amp;" )
        tp = tp.replace(  '<', '&lt;' )
        tp = tp.replace(  '>', '&gt;' )
        return "<pre>%s</pre>\n" %  tp

class Itemize( node_control ):
    def init(self, ws):
        items = ws.find_end_by_name("\stopitemize")
        self.tree = node_tree(items[1:-1])

    def html(  self ):
        return "\n<ul>\n%s\n</ul>\n" % self.tree.html()


class Item( node_control ):
    def html( self ):
        #if self.param:
        #    return '\n<li><b>%s</b>&nbsp;&nbsp;&nbsp;&nbsp;' % self.param[0].html()
        #TODO
        return '\n<li>'


class Goto( node_control ):

    def html( self ):
        return "&nbsp;<a href=%s >%s</a>&nbsp;" % (self.Params[1].html(), 
                self.Params[0].html())
        return ''

class Img( node_control ):
    def html( self ):
        #TODO 
        return "<img src=%s >" % (self.Param[0].html())

class Par( node_control ):
    def html( self ):
        return "<br />"


class starttable(node_control):
    def html( self ):
        return "<table>\n"

class stoptable(node_control):
    def html( self ):
        return "</table>\n"

class NC(node_control):
    def html( self ):
        return  "<tr><td>"

class AR(node_control):
    def html( self ):
        return  "</td></tr>\n"

class VL(node_control):
    def html( self ):
        return "</td><td>"

class VL(node_control):
    def html( self ):
        return "</td><td>"

class Bold(node_control):
    def html(self):
        if len(self.Params) > 0:
            return "<b>%s</b>" % self.Params[0].html()
        return ""

class Newline(node_control):
    def html(self):
        return "<br />\n"

NODE_MAP={ 
        '\section'       : Section,
        '\subsection'    : Section,
        '\subsubsection' : Section,
        '\starttyping'   : Typing,
        '\startitemize'  : Itemize,
        '\item'          : Item,
        '\goto'          : Goto,
        '\img'           : Img,
        '\par'           : Newline,
        '\starttable'    : starttable,
        '\stoptable'     : stoptable,
        '\NC'            : NC,
        '\VL'            : VL,
        '\AR'            : AR,
        '\\bold'         : Bold,
                }

class node_tree(list):
    def __init__(self, ws):
        w = None
        while True:
            w = ws.getword()
            if not w:
                return

            if w.type == Word.TYPE_PUNC:
                self.append(node_punc(ws))

            elif w.type == Word.TYPE_TEXT:
                self.append(node_text(ws))

            elif w.type == Word.TYPE_CPUNC:
                self.append(node_cpunc(ws))

            elif w.type == Word.TYPE_CONTROL:
                callback = NODE_MAP.get(w.name())
                if callback:
                    self.append(callback(ws))
                else:
                    ws.update()

    def html(self):
        for n in self:
            print n
            print "name:%s html:%s" % (
                    n.word.name().replace('\n', '\\n').replace(' ', '\\ '),
                    n.html().replace('\n', '\\n').replace(' ', '\\ ')
                    )
        return ''

        h = [n.html() for n in self]
        return ''.join(h)


f = codecs.open(sys.argv[1], 'r','utf8')
s = f.read()
words = split(s)
#show_word_details(words)
print node_tree(words).html()


        # end



if __name__ == "__main__":
    pass


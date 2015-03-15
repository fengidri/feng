# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-03-15 17:52:26
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
import logging
from words import Word
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

        elif self.name == ' ':
            ws.find_same(' ')
            self.h =  ' '

        elif self.name == '\n':
            if len(ws.find_same('\n')) > 1:
                self.h = "</p>\n\n<p>"

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

        #list.__init__(self)
        self.word = ws.getword()
        self._getattrs(ws)
        self._getparams(ws)
        self.init(ws)

    def init(self, ws):
        ws.update()

    def html(self):
        return ''
    def _getparams(self, ws): # 得到参数, 参数可以有多个, {}
        self.__get_params_or_attrs(ws, '{', '}', self.Params)

    def _getattrs(self, ws): # 得到属性, 也可以有多个, []
        self.__get_params_or_attrs(ws, '[', ']', self.Attrs)

    def __get_params_or_attrs(self, ws, s, e, cb):
        cr_num = 0
        while True:
            ws.update()
            word = ws.getword()
            if not word:
                break

            name = word.name()

            # 序列后的空格可以被吃掉,  同样参数后的空格也会被吃掉
            if name == ' ': continue

            #但是回车只能吃一个空格
            if name == '\n':
                if cr_num == 0:
                    cr_num += 1
                else:
                    ws.back()
                    break

            if name == s:
                ps = ws.find_end_by_name(e)
                p = node_tree(ps.slice(1, -1))
                cb.append(p)
                cr_num = 0# 一个参数后, 可以再吃一个空格
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

        h = "</p>\n<h%s>%s</h%s><p>\n" % (level, c, level)
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
        _ws = ws.find_end_by_name("\stopitemize")
        self.tree = node_tree(_ws.slice(1, -1))

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
        return "</p>\n\n<p>"

class DefHandle(node_control):
    MAPS = {}
    def init(self, ws):
        ws.update()
    def html(self):
        name = self.word.name()
        de = self.MAPS.get(name)
        if not de:
            raise Exception("Dont kwow: %s" % name)
        return de.Params[0].html()

class Def(node_control):
    def init(self, ws):
        while True:
            ws.update()
            word = ws.getword()
            name = word.name()
            if name in ['\n', ' ']:
                continue
            if word.type == Word.TYPE_CONTROL:
                self._getattrs(ws)
                self._getparams(ws)
                DefHandle.MAPS[name] = self
                break

    def html(self):
        return ''


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
        '\\def'          : Def
                }

class node_tree(list):
    def __init__(self, ws):
        msg = "ws.pos:%s word.line:%s  word.name:%s"
        while True:
            w = ws.getword()
            if not w:
                return
            logging.debug(msg, ws.pos, w.pos[0], w.name())

            if w.type == Word.TYPE_PUNC:
                self.append(node_punc(ws))

            elif w.type == Word.TYPE_TEXT:
                self.append(node_text(ws))

            elif w.type == Word.TYPE_CPUNC:
                self.append(node_cpunc(ws))

            elif w.type == Word.TYPE_CONTROL:
                callback = NODE_MAP.get(w.name())
                if not callback:
                    callback = DefHandle
                self.append(callback(ws))

    def html(self):
        #if Config.NodesList:
        #   for n in self:
        #       print n,
        #       print "name:%s html:%s line:%s" % (
        #               n.word.name().replace('\n', '\\n').replace(' ', '\\ '),
        #               n.html().replace('\n', '\\n').replace(' ', '\\ '),
        #               n.word.pos[0]
        #               )
        #   return ''

        h = [n.html() for n in self]
        return ''.join(h)


if __name__ == "__main__":
    pass


#encoding:utf8
#author:   丁雪峰
#file:     context
#description:  把context文件转换成html文件

#我试过很多次写这个功能的脚本,一开始还是什么都不明白的时候呢(^_^)
#一开始还是在大学的时候呢.用的是正则的方式,对于typing之类的没有办法处理
#也做过对于typing进行保护的方法
#后来也试过别的方法

#上一次的在工作之后的一段时候的一个周末,学习了一些词法分析的东西.
#效果当然还是不错的,但是代码的质量并不高,对于python的运用也是很简单的一种方式

#这一次的目的是使用的类的方法进行词法与语法分析,
#语法分析的结果中引入控制序列(tex中就是这么说的)对象
#控制序列会对于参数之类的东西进行主动的处理
#                                           -- 11.27
#bugs:
#2013年12月13日 星期五
#+   1.文件开头注释,之后的section 会被吃掉
#+   2.item 之后的换行, 不能正确放到<p></p>中

################################################################################
# 最近在写程序里两次用到的模式化的编程. 核心思想都是把数据与程序分开.
# 这两次分别是在b2bua里处理redis与在libSystem 中编写redis接口时出现的.
# 解决的问题:
#
################################################################################

import sys
import codecs
import re

#自定义的异常
class NextExcept( Exception ):
    """期待下一个对象,没有找到"""
    def __init__( self, value):
        self.value=value
    def __str__( self ):
        return repr( self.value )

#词法对象
class wnode( object ):
    META = 1

    ct_type=''#text command 
    wnode_name = ''
    content=''
    start=0   #对象在 source中位置
    end=0     #

    # 1 段内元素,默认, 
    #2 章节, 
    #3 分段元素
    paragraph=1
    def __init__(self, source, name, start = 0, end = 0):
        self.source = source
        self.line = source.line_nu
        self.col = source.column_nu
        self.wnode_name = self.name = name
        self.start = start
        self.end = end

class control_seq( object ):
    def Enter( self ):
        self.start = self.lexal.pos
        del self.buffer[ : ]

    def Leave( self ):
        control_seq=''.join( self.buffer )
        tmp = wnode( )
        tmp.wnode_name = ''.join( self.buffer )
        tmp.start = self.start 
        tmp.end = self.lexal.pos
        self.lexal.wnodes.append( tmp )
        self.lexal.back( )

    def __init__( self, lexicalanalysis):
        self.lexal = lexicalanalysis
        self.buffer = [  ]

    def in_fsm( self ):
        char = self.lexal.char( )

        if (not char.islower()) and  char != '\\' and (not char.isupper()):
            self.lexal.status = 'text'
            return 0

        self.buffer.append( char )

class punc( object ):
    '''
    处理特殊符号'%','#','$','&','{','}', '\n','[',']' 
    对于换行符的处理比较特殊
    '''
    def __init__( self, lexicalanalysis):
        self.lexal = lexicalanalysis
        self.buffer = [  ]
    def Enter( self ):
        self.start = self.lexal.pos
        del self.buffer[ : ]
        self.nu_newline = 0
        self.newline_flag = 0
    def Leave( self ):
        if self.newline_flag == 1:
            wnode_name = 'newline'
            tmp = wnode( )
            tmp.wnode_name = wnode_name 
            tmp.start = self.start 
            tmp.end = self.lexal.pos
            self.lexal.wnodes.append( tmp )


            if self.nu_newline > 1:

                wnode_name = '\par'
                tmp = wnode( )
                tmp.wnode_name = wnode_name 
                tmp.start = self.start 
                tmp.end = self.lexal.pos
                self.lexal.wnodes.append( tmp )

            self.lexal.back( )
        else:
            wnode_name = self.buffer[ 0 ]
            tmp = wnode( )
            tmp.wnode_name = wnode_name 
            tmp.start = self.start 
            tmp.end = self.lexal.pos
            self.lexal.wnodes.append( tmp )
    def in_fsm( self ):
        char = self.lexal.char( )


        if char == '\n':
            self.newline_flag = 1
        else:
            self.lexal.status = 'text'

        if self.newline_flag == 1:
            if char != '\n':
                self.lexal.status = 'text'
            else:
                self.nu_newline += 1

        self.buffer.append( char )

class text( object ):
    """
    处理文本
    """
    def __init__( self, lexicalanalysis):
        self.lexal = lexicalanalysis
        self.start = 0
        self.start_flag = 1
    def Enter( self ):
        self.start = self.lexal.pos
        self.start_flag = 1

    def Leave( self ):
        pos = self.lexal.pos
        if  pos > self.start + 1:

            tmp = wnode( )
            tmp.content = self.lexal.source[ self.start: pos - 1 ]
            tmp.wnode_name = 'text'
            tmp.start = self.start 
            tmp.end = pos
            self.lexal.wnodes.append( tmp )
        self.lexal.back( )


    def in_fsm( self ):
        char = self.lexal.char( )

        if self.start_flag == 1:
            if char.isspace( ):
                return 0
            else:
                self.start = self.lexal.pos
                self.start_flag = 0




        if char == '\\':
            self.lexal.status = 'control_seq'

        if char in ['%','#','$','&','{','}', '\n','[',']' ]:
            self.lexal.status = 'punc'



class Source(object):
    def __init__(self, source):
        self.source = source
        self.lenght = len(source)
        self.pos =  0
        self.line_nu = 1
        self.column_nu = 0  #可以是负数, 表示从\n 开始反向计算的
        self.__save_pos = None
    def save_pos(self):
        self.__save_pos = (self.pos, self.line_nu, self.column_nu)
    def get_save(self):
        return self.__save_pos

    def char( self):
        if self.pos >= self.lenght:
            return None
        return self.source[ self.pos ]
    def gettext(self, start, end):
        return self.source[start: end]

    def back( self ):
        self.pos -= 1
        c = self.char()
        if c == "\n":
            self.line_nu -= 1
            self.column_nu = -1
        else:
            self.column_nu -= 1
        return c

    def next(self):
        c = self.char()
        if c == "\n":
            self.line_nu += 1
            self.column_nu = 0
        else:
            self.column_nu += 1

        self.pos += 1
        c = self.char()
        return c
    def get_pos(self):
        return self.pos


#词法分析

class lexicalanalysis:
    TEX_CHAR = ['%','#','$','&','{','}', '^', '_', '~', '[', ']', ' ',
            '\n']
    def __init__(self, source):
        self.source = Source(source)
        self.wnodes = []
        self.start = 0

        self.fsm = {}
        self.fsm['comment'] = self.fsm_comment
        self.fsm['control'] = self.fsm_control
        self.fsm['text'] = self.fsm_text
        self.fsm['meta']= self.fsm_meta

        self.fsm_scan_source()
    def change_to_meta(self):
        self.status = "meta"
        self.source.save_pos()

    def change_to_text(self, offset=0):
        self.status = "text"
        self.source.save_pos()
        self.start = self.source.get_pos() + offset

    def change_to_control(self):
        self.source.save_pos()
        self.cnbuf = ['\\']
        self.endwhite = False
        self.status = "control"

    def change_to_comment(self):
        self.status = "comment"
    def fsm_meta(self, char):
        self.wnodes.append(wnode(self.source, char))
        self.change_to_text(1)

    def fsm_comment(self, char):
        if char == '\n':
            self.change_to_text()

    def fsm_control(self, char):
        if len(self.cnbuf) == 1 and  char in self.TEX_CHAR:
            w = wnode(self.source, '\\%s' % char)
            self.wnodes.append(w)
            self.change_to_text()
            return

        elif self.endwhite == False and (char.islower() or char.isupper()):
            self.cnbuf.append(char)
            return

        elif char == ' ':
            self.endwhite = True
            self.cnbuf.append(char)
            return

        w = wnode(self.source, ''.join(self.cnbuf).strip())
        self.wnodes.append(w)
        if char == '%':
            self.change_to_comment()
        elif char == '\\':
            self.change_to_control()
        elif char == '\n':
            self.change_to_text(1)
        else:
            self.change_to_text()
            self.source.back()
    def __add_text_node(self):
        end = self.source.get_pos() - 1 
        if end - self.start >= 0:
            w = wnode(self.source, 'text', self.start, end)
            self.wnodes.append(w)

    def fsm_text(self, char):
        if char == '\\':
            self.change_to_control()
            self.__add_text_node()
        elif char == '%':
            self.change_to_comment()
            self.__add_text_node()
        elif char in self.TEX_CHAR:
            self.__add_text_node()
            self.change_to_meta()
            self.source.back()




    def fsm_scan_source( self ):
        self.change_to_text()

        c  = self.source.char()
        while c:
            self.fsm[self.status](c)
            c = self.source.next()
        if self.status == "text":
            self.fsm[self.status]('\\')
        elif self.status == 'control':
            self.fsm[self.status]('\n')




class node(object):
    def __init__( self, lex ):
        self.sub_node=[  ] #对于section, typing之类的可以有子树的
        self.text=''#用于text类, 用于保存内容
        self.param=[  ]#用于保存参数, 由于可以有多个参数组,所以使用list
        self.enode = None
        self.start = lex.wnode().start


        #lex是记法分析得到的结果, 其中包含有一些, 对应的操作方法
        self.lex = lex
        self.init_node( )
        self.name = self.lex.wnode( ).wnode_name
        self.wnode = lex.wnode()


class origin_node( node ):#控制序列 父类
    """
      对于wnode进行处理的基础类,包含一些基本的处理wnode的方法
    """
    endnode = None
    def __init__( self, lex ):
        node.__init__(self, lex)
        self.get_param( )
    def init_node( self ):
        #对于继承的类的处理的内容放到这个函数中进行
        pass

    def get_param( self ):
        """
        针对于secton之类的控制序列


        提取控制序列后以[]或以{}包围起来的参数,
        放到self.param与 self.sub_node 中
        以[]包围的放到param中去
        以{}包围的放到了sub_node中,与area的作用相同.
        """

        while True:
            next_wnode = self.lex.next_wnode( )
            if not next_wnode:
                break
            if next_wnode.name in [' ', '\n']:
                continue

            if next_wnode.wnode_name== '[':
                self.param += create_quene(self, self.lex, endflag = ']' )
                continue

            if next_wnode.wnode_name== '{':
                self.sub_node += create_quene( self, self.lex, endflag = '}' )
                continue
            break

        #在循环中由于先取下一位之后再进行比较运算
        #所以要回退一步
        self.lex.offset_back( )
        if not self.endnode:
            return
        self.sub_node = create_quene(self, self.lex, endflag = self.endnode)
        self.enode = self.lex.wnode( )



class Text( node ):
    def init_node( self ):
        self.text = self.lex.wnode( ).content

    def node_info( self ):
        print self.text

    def html( self ):
        return  self.text.replace('&', "&amp;" ).replace(  '<', '&lt;' ).replace(  '>', '&gt;')

    def plain( self ):
        self.text = re.sub( '\n\s*\n[\n\r\s]*','</p><p>\n', self.text)
        return self.text



class Section( origin_node ):


    def sub_html( self ):
        return ''.join([ obj.plain() for obj in self.sub_node ])

    def node_info( self ):
        print self,
        for node in self.sub_node:
            node.node_info

    def html( self ):

        return "<h3>%s</h3>\n" % self.sub_html( )
        

class Subsection( Section ):
    def html( self ):
        return "<h4>%s</h4>\n" % self.sub_html( )

class Subsubsection( Section ):
    def html( self ):
        return "<h5>%s</h5>\n" % self.sub_html( )

class Typing( origin_node ):
    endnode = "\stoptyping"
    def html( self ):
        area_typing = self.lex.source.gettext(self.sub_node[0].start , self.enode.start)
        area_typing = area_typing.replace('&', "&amp;" ).replace(  '<', '&lt;' ).replace(  '>', '&gt;' )
        return "<pre>%s</pre>\n" % area_typing

class Itemize( origin_node ):
    endnode = '\stopitemize'

    def html(  self ):
        tmp = [ '<ul>' ]
        p_nu = 0 #item之后的第几段
        item_nu = 0 #第几个item

        for node in self.sub_node:

                
            if node.name == '\item':
                if item_nu != 0:
                    tmp.append( '</li>' )
                tmp.append( node.html() )
                p_nu = 0
                item_nu += 1
                continue
            tmp.append( node.html() )
        if item_nu > 0:
            tmp.append( '</li></ul>\n' )
        return ''.join( tmp )


class Item( origin_node ):
    def html( self ):
        if self.param:
            return '\n<li><b>%s</b>' % self.param[0].html()
        return '\n<li>'

class Percent( origin_node ):
    endnode = "newline"
    def html( self ):
        return ''

class Goto( origin_node ):
    def html( self ):
        if len(self.param)< 2:
            raise Exception("Goto except two args")
        return "<a href=%s >%s</a>" % (self.param[1].html(),
                self.param[0].html())
class Img( origin_node ):
    def html( self ):
        if len(self.param)< 1:
            raise Exception("Img except one arg(url)")
        return "<img src=%s >" % (self.param[0].html())

class Par( origin_node ):
    def html( self ):
        return "<br />"

class Newline( node ):

    def init_node( self ):
        nu = 1
        while True:
            wnode = self.lex.next_wnode( )
            if not wnode:
                break

            if wnode.wnode_name == '\n':
                nu += 1
            else:
                break
        self.lex.offset_back( )
        self.nu = nu

    def html( self ):
        if self.nu > 1:
            return "</p><p>"
        else:
            return ""

class starttable(origin_node):
    def html( self ):
        return "<table>\n"

class stoptable(origin_node):
    def html( self ):
        return "</table>\n"

class NC(origin_node):
    def html( self ):
        return  "<tr><td>"

class AR(origin_node):
    def html( self ):
        return  "</td></tr>\n"

class VL(origin_node):
    def html( self ):
        return "</td><td>"

class VL(origin_node):
    def html( self ):
        return "</td><td>"
class Bold(origin_node):
    def html(self):
        if len(self.sub_node) > 0:
            return "<b>%s</b>" % self.sub_node[0].html()
        return ""

NODE_MAP={ 
        'text'           : Text,
        '\section'       : Section,
        '\subsection'    : Subsection,
        '\subsubsection' : Subsubsection,
        '\starttyping'   : Typing,
        '\startitemize'  : Itemize,
        '\item'          : Item,
        '\goto'          : Goto,
        '\img'          : Img,
        '\par'         :Newline,
        '\starttable'         :starttable,
        '\stoptable'         :stoptable,
        '\NC'            :NC,
        '\VL'            :VL,
        '\AR'            :AR,
        '\\bold'            :Bold,

        '%'              : Percent,
        '\n'             : Newline
                }
class _lex( object ):
    """
    控制一lex,提供对于lex序列进行操作的接口
    """
    def __init__(self, lexicalanalysis):
        self.tree_trunk=[  ]

        self.node_class=[  ]
        self.NODE_MAP={ }
        self.pos = -1

        self.lex = lexicalanalysis.wnodes
        self.source = lexicalanalysis.source

    def see_next_wnode( self ): # 返回下一个对象, 不使记录偏移
        try:
            return  self.lex[ self.pos + 1 ]
        except IndexError, e:
            return None
    def next_wnode( self ): # 返回下一对象, 并使记录偏移
        self.pos += 1
        try:
            return  self.lex[ self.pos ]
        except IndexError, e:
            return None

    def wnode( self ): #返回当前对象
        return  self.lex[ self.pos ]

    def offset_back( self ):
        self.pos -= 1




"""
 模型:


                                           [<node:starttyping>,<node:text>,<node:stoptyping>]
                                           |
                                           |
[<node:text>, <node:section>, <node:text>, <node:typing>, <node:text>] 
              |
              |
              [<node:Group_pre>,<node:text>,<node:Group_post>]



"""
def create_quene(fa, lex, endflag = None ): # 不包含起止节点
    tmp=[  ]

    while True:
        wnode = lex.next_wnode( )
        if wnode == None:#历遍完成
            raise Exception("%s:%s:%s except %s"  % (fa.name,
                fa.wnode.line, fa.wnode.col, endflag))

        if wnode.wnode_name == endflag:#到达结束flag
            break

        c = NODE_MAP.get( wnode.wnode_name)
        if c == None:
            #TODO
            pass
        else:
            tmp.append( c(lex) )
    return tmp

class Paragraph( object ):
    """
    生成一个文章的主体,这个主体由段与章节号组成.
    一个指导性的思想是:
          以生成段对象为主. 段对象包含有一个sub_node.其中包含有段内的各种元素.


    对于wnodes进行分析, 所有的段内元素组成一个list, 非段内元素单独一个wnode对象.
    这个list与wnode放到trunk中.


    """
    def __init__( self, lex ):
        tmp=[  ]
    
        lex.offset_back( )
        while True:
            wnode = lex.next_wnode( )
            if wnode == None:#历遍完成
                break
    
            if wnode.paragraph > 1:
                lex.offset_back( )
                break
    
            c = NODE_MAP.get( wnode.wnode_name)
            if c == None:
                #TODO
                pass
            else:
                tmp.append( c(lex) )

        self.sub_node=tmp
    def html( self ):
        text = ''.join( [obj.html() for obj in self.sub_node  ]) 
        return "<p>%s</p>\n"  % text
    

    
def create_trunk( lex ):
    tmp=[  ]

    while True:
        wnode = lex.next_wnode( )
        if wnode == None:#历遍完成
            break
        
        if wnode.paragraph == 1:
            c = Paragraph 
        else:
            c = NODE_MAP.get( wnode.wnode_name)
        if c == None:
            #TODO
            pass
        else:
            tmp.append( c(lex) )
    return tmp



def context2html(contextfile, htmlfile=None):
    f = codecs.open(contextfile, 'r','utf8')
    s = f.read()
    f.close()


    lex = lexicalanalysis(s)
    print len(lex.wnodes)
    #for w in lex.wnodes:
    #    if w.name == 'text':
    #        print 'text', w.start, w.end,w.source.gettext(w.start, w.end+1),"|"
    #    else:
    #        print w.name, w.line, w.col
 
    #return
    xlex = _lex(lex)


    trunk = create_trunk( xlex )
    html =  ''.join( [node.html() for node in trunk] )

    if not htmlfile:
        return html
    f = codecs.open(htmlfile, 'w','utf8')
    f.write(html)
    f.close()



if __name__  == '__main__':
    if len(sys.argv) == 1:
        print """
        this script can trasfer context file to html
        usage:
             context contexfile  htmlfile
        """
    if len( sys.argv) == 2:
        print context2html(sys.argv[1], None)
    else:
        context2html(sys.argv[1], sys.argv[2])

    



















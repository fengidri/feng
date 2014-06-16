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
    ct_type=''#text command 
    wnode_name = ''
    content=''
    start=0   #对象在 source中位置
    end=0     #

    # 1 段内元素,默认, 
    #2 章节, 
    #3 分段元素
    paragraph=1

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

        if (not char.islower()) and  char != '\\':
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




#词法分析

class lexicalanalysis:
    def __init__(self, source):
        """
        这些字符是要处理的一些 [词] 的开头,当遇到这些字符时要进行处理.
        在词法分析过程中,这些要处理的对象在处理时只考虑其本身并不考虑其它相关的
        内容.

        """
        self.fsm_map={ 
                'control_seq': control_seq(self),
                'punc': punc( self ),
                'text':text( self )
                }

        self.wnodes = []
        self.source = source
        self.pos = -1
        self.status ='text'
        self.status_save='text'
        self.fsm=self.fsm_map[ 'text' ]

        self.fsm_scan_source()
        self.set_paragraph( )
    def set_paragraph( self ):
        for wnode in self.wnodes:
            if wnode.wnode_name == '\par':
                wnode.paragraph = 2

            if re.search(r'^\\(sub)*section$' , wnode.wnode_name):
                wnode.paragraph = 3

            if wnode.wnode_name == '\chapter':
                wnode.paragraph = 3


    def char( self):
        return self.source[ self.pos ]

    def fsm_scan_source( self ):
        length = len( self.source ) -1
        while self.pos < length:
            self.pos += 1
            if self.status != self.status_save:
                self.status_save =self.status
                self.fsm.Leave( )
                self.fsm= self.fsm_map.get( self.status )
                self.fsm.Enter( )
            self.fsm.in_fsm( )
        self.fsm.Leave( )
    def back( self ):
        self.pos -= 1






class origin_node( object ):
    """
      对于wnode进行处理的基础类,包含一些基本的处理wnode的方法
    """
    def __init__( self, lex ):
        self.sub_node=[  ] #对于section, typing之类的可以有子树的
        self.text=''#用于text类, 用于保存内容
        self.param=[  ]#用于保存参数, 由于可以有多个参数组,所以使用list

        #如果为None,不进行下一个节点的检查, 不为None时
        #进行下一个节点的检查,要求其wnode_name为指定的内容,否则出现异常
        self.next_content = None  

        #lex是记法分析得到的结果, 其中包含有一些, 对应的操作方法
        self.lex = lex
        self.init_node( )
        self.name = self.lex.wnode( ).wnode_name
    def init_node( self ):
        #对于继承的类的处理的内容放到这个函数中进行
        pass

    def next_check( self ):
        if self.next_content:
            wnode_name = self.lex.see_next_wnode( ).wnode_name
            if wnode_name != self.next_content:
                raise NextExcept( wnode_name )
        return 0

    def get_param( self ):
        """
        针对于secton之类的控制序列


        提取控制序列后以[]或以{}包围起来的参数,
        放到self.param与 self.sub_node 中
        以[]包围的放到param中去
        以{}包围的放到了sub_node中,与area的作用相同.
        """
        self.param = [  ]
        self.content = [ ]

        while True:
            next_wnode = self.lex.next_wnode( )

            if next_wnode.wnode_name== '[':
                self.param = create_quene( ']' )
                continue

            if next_wnode.wnode_name== '{':
                self.sub_node = create_quene( self.lex, endflag = '}' )
                continue
            break

        #在循环中由于先取下一位之后再进行比较运算
        #所以要回退一步
        self.lex.offset_back( )

    def get_area( self, end_name ):
        """
        针对于typing之类的控制序列
        """
        self.sub_node = create_quene( self.lex, endflag = end_name)


class Text( origin_node ):
    def init_node( self ):
        self.text = self.lex.wnode( ).content

    def node_info( self ):
        print self
        print self.text

    def html( self ):
        return "%s" % self.text

    def plain( self ):
        self.text = re.sub( '\n\s*\n[\n\r\s]*','</p><p>\n', self.text)
        return self.text



class Section( origin_node ):
    def init_node( self ):
        self.next_check( )
        self.get_param( )

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
    def init_node( self ):
        self.endflag = '\stoptyping'
        area_start = self.lex.wnode( ).start + len( '\starttyping')
        while True:
            wnode = self.lex.next_wnode( )
            if wnode == None:
                raise NextExcept( self.endflag )

            if wnode.wnode_name == self.endflag:
                break
        area_end = self.lex.wnode( ).start


        self.area_typing = self.lex.source[ area_start: area_end ]
    def html( self ):
        self.area_typing = self.area_typing.replace(  '<', '&lt;' )
        self.area_typing = self.area_typing.replace(  '>', '&gt;' )
        return "<pre>%s</pre>\n" % self.area_typing

class Itemize( origin_node ):
    def init_node( self ):
        self.get_area( '\stopitemize' )
        

    def html(  self ):
        tmp = [ '<ul>' ]
        p_nu = 0 #item之后的第几段
        item_nu = 0 #第几个item

        for node in self.sub_node:
            if node.name == 'text':
                if p_nu == 0:
                    tmp.append( node.plain() )
                else:
                    tmp.append( node.html() )
                continue
                
            if node.name == '\item':
                if item_nu == 0:
                    tmp.append( '<li>' )
                else:
                    tmp.append( '</li>\n<li>' )
                p_nu = 0
                item_nu += 1
                continue
            tmp.append( node.html() )
        if item_nu > 0:
            tmp.append( '</li></ul>\n' )
        return ''.join( tmp )


class Item( origin_node ):
    def init_node( self ):
        pass

    def html( self ):
        return '</li>\n<li>'

class Percent( origin_node ):
    def init_node( self ):
        while True:
            wnode = self.lex.next_wnode( )

            if wnode.wnode_name == 'newline':
                break
    def html( self ):
        return ''

class Newline( origin_node ):
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





NODE_MAP={ 
        'text'           : Text,
        '\section'       : Section,
        '\subsection'    : Subsection,
        '\subsubsection' : Subsubsection,
        '\starttyping'   : Typing,
        '\startitemize'  : Itemize,
        '\item'          : Item,
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

    def see_next_wnode( self ):
        try:
            return  self.lex[ self.pos + 1 ]
        except IndexError, e:
            return None


    def next_wnode( self ):
        self.pos += 1
        try:
            return  self.lex[ self.pos ]
        except IndexError, e:
            return None

    def wnode( self ):
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
def create_quene( lex, endflag = None ):
    tmp=[  ]

    while True:
        wnode = lex.next_wnode( )
        if wnode == None:#历遍完成
            break

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



def context2html(contextfile, htmlfile):
    f = codecs.open(contextfile, 'r','utf8')
    s = f.read()
    f.close()


    xlex = _lex(lexicalanalysis( s ))


    trunk = create_trunk( xlex )
    html =  ''.join( [node.html() for node in trunk] )

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
        f = codecs.open(sys.argv[1], 'r','utf8')
        s = f.read()
        f.close()
        lexicalanalysis( s )
        #xlex = _lex()

        print '--------------------'

        #trunk = create_quene( xlex )
        #html =  ''.join( [node.html() for node in trunk] )
        #
        #f = codecs.open('test.html', 'w','utf8')
        #f.write(html)
        #f.close()



    else:
        context2html(sys.argv[1], sys.argv[2])

    


















#if char in self.node_start:

#if self.status == 0:#normal
#    callback = self.callback.get(char)
#    if callback:
#        callback()
#    else:
#        #普通文本
#        self.buf.append(char)

#elif self.status == 1:#typing
#    if source[self.pos: len(endgroup)  + self.pos]  == endgroup:
#        self.normal()
#        self.status = 2
#    self.buf.append(char)

#elif self.status == 2:#waiting for command end
#    self.buf.append(char)

#    n_char = source[self.pos  + 1]

#    if not n_char.isalpha():
#        command  = ''.join(self.buf)
#        self.buf = []
#        if command in self.start_typing:
#            index = self.start_typing.index(command)
#            endgroup  = self.end_typing[index]
#            self.lex.append( ('starttyping', command) )
#            self.status = 1
#        elif command in self.end_typing:
#            self.lex.append( ('endtyping', command) )
#            self.status = 0
#        else:
#            self.status = 0
#            command_type = self.command_type.get(command, 
#                    u'command')
#            self.lex.append( (command_type, command) )

#elif self.status == 4:#换行符
#    if char == '\n':
#        self.line_break_nu += 1
#    elif char == '\r':
#        pass
#    else:
#        if self.line_break_nu > 1:
#            self.normal()
#            self.lex.append( (u'par', ur'\par') )
#        else:
#            self.buf.append(' ')
#        self.line_break_nu == 0
#        self.status = 0
#        self.pos  -= 1



#def line_break(self):
#    self.status = 4
#    self.line_break_nu = 1


#def percent(self):
#    #注释
#    self.status = 3
#def back_slash(self):
#    #命令
#    char = self.source[self.pos + 1]
#    if  char in "$#%&{}^_~ ":#符号输出
#        self.buf.append(char)
#        return 0
#    else:
#        self.normal()
#        self.status = 2
#        char = self.source[self.pos]
#        self.buf.append(char)
#def pre_brace(self):
#    self.normal()
#    self.lex.append( ('begingroup', '{') )
#def post_brace(self):
#    self.normal()
#    self.lex.append( ('endgroup', '}') )
#        


#def normal(self):
#    if self.buf ==  ['\n']:
#        self.buf = []
#        return 0
#    
#    if len(self.buf) >0:
#        self.lex.append( ('text', u''.join(self.buf) ) )
#        self.buf = []
#        return 0
#class tree( object ):
#    def __init__( self, lex ):
#        self.lex = lex( )
#
#
#
#
#
#
#
#        
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#        self.tree = []
#        self.deep = []
#        self.deep.append(self.tree)
#        self.lex  = lex
#
#        self.callback = {
#                'text':self.text,
#                'chapter':self.sections,
#                'section':self.sections,
#                'subsection':self.sections,
#                'subsubsection':self.sections,
#                'subsubsubsection':self.sections,
#                'typing':self.typing,
#                }
#
#        lenght  = len(lex)  - 1
#        self.pos =  -1
#
#        while self.pos <  lenght:
#            self.pos   += 1
#
#            self.element = lex[self.pos]
#            callback = self.callback.get(element[0])
#            if callback:
#                callback()
#
#    def text(self):
#        self.deep[ -1].append(self.element)
#
#    def sections(self):
#        section = [self.element]
#        self.deep[ -1].append(section)
#
#        if self.next_el()[0]  == 'begingroup' and \
#                self.next_el(2)[0]  == 'endgroup':
#                    section.append(self.next_el(1))
#
#    def itemize(self):
#        pass
#
#    def typing(self):
#        typing = [self.element]
#        self.deep[-1].append(typing)
#
#        if self.next_el()[0]  == 'begin_typing' and \
#                self.next_el(2)[0]  == 'end_typing':
#                    section.append(self.next_el(1))
#
#    def next_el(self, s = 1):
#        return self.lex(self.pos  + s)
#
#
#class lex2html:
#    def __init__(self, lex):
#        self.lex = lex
#        self.out = []
#        self.endgroup_stack = []
#
#        self.callback = { 
#                u'chapter':self.chapter,
#                u'section':self.section,
#                u'subsection':self.subsection,
#                u'subsubsection':self.subsubsection,
#                u'startitemize':self.startitemize,
#                u'stopitemize':self.stopitemize,
#                u'item':self.item,
#                u'starttyping':self.starttyping,
#                u'endtyping':self.endtyping,
#                u'begingroup':self.begingroup,
#                u'endgroup':self.endgroup,
#                u'text':self.text,
#                u'par':self.par
#                }
#        for self.element in lex:
#            callback =  self.callback.get(self.element[0])
#            if callback:
#                callback()
#    def html(self):
#        return ''.join(self.out)
#    def chapter(self):
#        self.begingroup = u'</p>\n<h2>'
#        self.endgroup_stack.append(u'</h2>\n<p>')
#    def section(self):
#        self.begingroup = u'</p>\n<h3>'
#        self.endgroup_stack.append(u'</h3>\n<p>')
#    def subsection(self):
#        self.begingroup = u'</p>\n<h4>'
#        self.endgroup_stack.append(u'</h4>\n<p>')
#    def subsubsection(self):
#        self.begingroup = u'</p>\n<h5>'
#        self.endgroup_stack.append(u'</h5>\n<p>')
#    def par(self):
#        self.out.append(u'\n</p>\n<p>')
#    def startitemize(self):
#        self.out.append(u'<ul>\n')
#        self.startitem = 0
#    def stopitemize(self):
#        self.out.append(u'</li>\n</ul>\n')
#    def item(self):
#        if self.startitem ==  0:
#            self.out.append(u'<li>')
#            self.startitem = 1
#        else:
#            self.out.append(u'</li>\n<li>')
#    def starttyping(self):
#        self.out.append(u'<pre>')
#    def endtyping(self):
#        self.out.append(u'</pre>')
#    def begingroup(self):
#        self.out.append(self.begingroup)
#    def endgroup(self):
#        self.out.append(self.endgroup_stack.pop())
#    def text(self):
#        self.out.append(self.element[1])
#
#def context2html(contextfile, htmlfile):
#    f = codecs.open(contextfile, 'r','utf8')
#    s = f.read()
#    f.close()
#
#    c = lexicalanalysis(s) 
#    html = lex2html(c.lex)
#
#    f = codecs.open(htmlfile, 'w','utf8')
#    f.write(html)
#    f.close()
#        
#     
#
#    # 列遍文本
#    def scan_source(self, source):
#        pos =  -1
#        lenght = len(source)  - 1
#        wnodes=[  ]
#
#        start = 0#描述text的开始
#
#        while pos < lenght:
#            pos  += 1
#            char = source[pos]
#
#            #跳过source或一个控制序列之后的空格
#            if pos == start and char in ' \t':
#                start += 1
#                continue
#            #状态
#
#            callback = self.node_start.get( char )
#            if not callback:
#                continue
#
#            if pos > start :
#                tmp=wnode( )
#                tmp.content= source[ start : pos ]
#                tmp.start=start
#                tmp.wnode_name = 'text'
#                wnodes.append( tmp )
#
#            tmp=wnode( )
#            tmp.start= pos
#            callback( tmp ) 
#            start = tmp.end
#
#            wnodes.append( tmp )
#
#            pos = start - 1
#
#        tmp=wnode( )
#        tmp.content= source[ start : pos ]
#        tmp.ct_type= 'text'
#        tmp.wnode_name = 'text'
#
#        wnodes.append( tmp )
#        self.wnodes = wnodes
#
#    def get_contrl( self, tmp ):#\
#        "处理控制序列"
#        start = tmp.start
#        point= start + 1
#
#        try:
#            "start 指向 \ "
#            char = self.source[ point ]
#            if char in  "$#%&{}^_~ ":#符号输出
#                contrl=self.source[ start: start + 2 ]
#            else:
#                while self.source[ point ].islower( ):
#                    point = point + 1
#                contrl=self.source[ start: point ]
#        except Exception, e:
#            print e
#            pass
#
#        tmp.wnode_name = contrl
#        tmp.end = point
#
#
#def punc( self , tmp):
#    "处理特殊符号"
#    "跳过空格"
#    char = self.source[ tmp.start ]
#    if char == '\n':
#        try:
#            while
#  
#    tmp.wnode_name = char
#    tmp.end = tmp.start + 1

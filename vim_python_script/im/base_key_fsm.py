#encoding:utf8
import pyvim
import vim
import re
import imrc
import sqlite3
class Base_Fsm( object ):
    def __init__(self):
        self.key_map={ #{{{
            "1" : self.digit,
            "2" : self.digit,
            "3" : self.digit,
            "4" : self.digit,
            "5" : self.digit,
            "6" : self.digit,
            "7" : self.digit,
            "8" : self.digit,
            "9" : self.digit,
            "0" : self.digit,
            "A" : self.upper_letter,
            "B" : self.upper_letter,
            "C" : self.upper_letter,
            "D" : self.upper_letter,
            "E" : self.upper_letter,
            "F" : self.upper_letter,
            "G" : self.upper_letter,
            "H" : self.upper_letter,
            "I" : self.upper_letter,
            "J" : self.upper_letter,
            "K" : self.upper_letter,
            "L" : self.upper_letter,
            "M" : self.upper_letter,
            "N" : self.upper_letter,
            "O" : self.upper_letter,
            "P" : self.upper_letter,
            "Q" : self.upper_letter,
            "R" : self.upper_letter,
            "S" : self.upper_letter,
            "T" : self.upper_letter,
            "U" : self.upper_letter,
            "V" : self.upper_letter,
            "W" : self.upper_letter,
            "X" : self.upper_letter,
            "Y" : self.upper_letter,
            "Z" : self.upper_letter,
            "a" : self.lower_letter,
            "b" : self.lower_letter,
            "c" : self.lower_letter,
            "d" : self.lower_letter,
            "e" : self.lower_letter,
            "f" : self.lower_letter,
            "g" : self.lower_letter,
            "h" : self.lower_letter,
            "i" : self.lower_letter,
            "j" : self.lower_letter,
            "k" : self.lower_letter,
            "l" : self.lower_letter,
            "m" : self.lower_letter,
            "n" : self.lower_letter,
            "o" : self.lower_letter,
            "p" : self.lower_letter,
            "q" : self.lower_letter,
            "r" : self.lower_letter,
            "s" : self.lower_letter,
            "t" : self.lower_letter,
            "u" : self.lower_letter,
            "v" : self.lower_letter,
            "w" : self.lower_letter,
            "x" : self.lower_letter,
            "y" : self.lower_letter,
            "z" : self.lower_letter
            }
        self.punc_map={
            "(" : self.parenthess,
            "[" : self.bracket,
            "{" : self.brace,
            "'" : self.mark,
            "," : self.comma,
            ";" : self.semicolon,
            "-" : self.minus,
            "_" : self.underline,
            "+" : self.add,
            "%" : self.precent,
            "&" : self.and_,
            "<" : self.lt,
            ">" : self.gt,
            "^" : self.cat,
            "!" : self.not_,
            "." : self.dot,
            "/" : self.slash,
            "=" : self.eq,
            '"' : self.double_mark,
            'tab' : self.tab,
            'c-j' : self.c_j,
            'bs' : self.backspace,
            'cr' : self.enter,
            'space': self.space,
            'esc': self.esc
            }
            #}}}
    def Leave(self):
        pass
    def Enter(self):
        pass
    def in_fsm( self, key):
        self.key= key
        callback=self.key_map.get(key, self.punc)
        callback()
    def all_key( self ):
        keys=self.key_map.keys( )
        keys.extend( self.punc_map.keys())
        return keys

 
    def digit( self ):
        pyvim.feedkeys( self.key ,'n' )

    def upper_letter( self ):
        pyvim.feedkeys( self.key  ,'n' )

    def lower_letter( self ):
        pyvim.feedkeys( self.key ,'n'  )

    def punc(self):
        callback=self.punc_map.get( self.key, None)

        if callback:
            callback()

    def parenthess(self):
        pyvim.feedkeys("(" ,'n' )
    def bracket(self):
        pyvim.feedkeys('[' ,'n' )
    def brace(self):
        pyvim.feedkeys('{' ,'n' )
    def mark(self):
        pyvim.feedkeys("'" ,'n' )
    def comma(self):
        pyvim.feedkeys(',' ,'n' )
    def semicolon(self):
        pyvim.feedkeys(';' ,'n' )
    def minus(self):
        pyvim.feedkeys('-' ,'n' )
    def add(self):
        pyvim.feedkeys('+' ,'n' )
    def precent(self):
        pyvim.feedkeys('%' ,'n' )
    def and_(self):
        pyvim.feedkeys('&' ,'n' )
    def lt(self):
        pyvim.feedkeys('<' ,'n' )
    def gt(self):
        pyvim.feedkeys('>' ,'n' )
    def cat(self):
        pyvim.feedkeys('^' ,'n' )
    def not_(self):
        pyvim.feedkeys('!' ,'n' )
    def dot(self):
        pyvim.feedkeys('.' ,'n' )
    def underline( self ):
        pyvim.feedkeys('_' ,'n' )

    def slash(self):
        pyvim.feedkeys('/' ,'n' )
    def eq(self):
        pyvim.feedkeys('=' ,'n' )
    def double_mark(self):
        pyvim.feedkeys('"' ,'n' )
    def tab(self):
        pyvim.feedkeys('    ' ,'n' )

        
    def c_j(self):
        string=pyvim.str_after_cursor( )
        tag=r'\'"([{}])'

        n_list=[ ]
        for i in tag:
            t=string.find( i )
            if t > -1:
                n_list.append( t )

        if len( n_list ) > 0:
            pyvim.feedkeys( '\<right>' * ( min( n_list ) +1))

    def backspace(self):
        pyvim.feedkeys(r'\<BS>','n')
    def enter(self):
        pyvim.feedkeys(r'\<CR>' ,'n')
    def space(self):
        pyvim.feedkeys(r'\<space>', 'n')
    def esc( self ):
        pyvim.feedkeys('\<esc>' ,'n' )
        
class Base_Key_Fsm( Base_Fsm ):
    def tab(self):
        if pyvim.pumvisible():
            pyvim.feedkeys('\<C-n>' ,'n' )
        else:
            pyvim.feedkeys('    ' ,'n' )

class Base_Code_Fsm( Base_Fsm ):
    def tab( self ):
        if pyvim.pumvisible():
            pyvim.feedkeys('\<C-n>' ,'n' )
            return 0

        if re.search(r'^\s*$',pyvim.str_before_cursor( )):
            pyvim.feedkeys( '    ')
        else:
            pyvim.feedkeys('\<C-X>\<C-O>\<C-P>' )

    def bracket( self ):#[  ]
        if pyvim.str_after_cursor(  ) == '':
            pyvim.feedkeys( '[  ]', 'n')
            pyvim.feedkeys('\<left>\<left>')
        else:
            pyvim.feedkeys( '[', 'n')

    def parenthess( self ):#(  )
        if pyvim.str_after_cursor(  ) == '':
            pyvim.feedkeys('( )', 'n')
            pyvim.feedkeys('\<left>')
        else:
            pyvim.feedkeys('(', 'n')
    
    def brace( self ):#{  }
        if pyvim.str_after_cursor(  ) == '':
            if pyvim.str_before_cursor( ).endswith( ')'):
                pyvim.feedkeys( '\<cr>{\<cr>}\<up>\<cr>','n')
            else:
                pyvim.feedkeys( '{  }\<left>\<left>', 'n')
        else:
            pyvim.feedkeys('{', 'n')
    
    def mark( self ):
        if pyvim.str_after_cursor(  ) == '':
            pyvim.feedkeys("\<c-v>'\<c-v>'\<left>")
        else:
            pyvim.feedkeys("\<c-v>'")
    
    def double_mark( self ):
        str_after=pyvim.str_after_cursor(  )
        if  str_after == '':
            pyvim.feedkeys( r'""\<left>','n')
            return 0

        if str_after[0] == '"':
            pyvim.feedkeys( r'""\<left>','n')
            return 0

        pyvim.feedkeys( '"','n')
    def dot(self):
        if pyvim.str_before_cursor( ).endswith('.'):
            pyvim.feedkeys('\<bs>->' ,'n' )
        else:
            pyvim.feedkeys('.' ,'n' )

class _wubi_seach( object ):
    def __del__( self ):
        self.cu.close( )
        self.cx.close( )
    def __init__(self):
        self.cx=sqlite3.connect(imrc.wubi_db)
        self.cu=self.cx.cursor()
        self.cache={  }


    def search( self , buf):
        '得到备选的字词'

        patten = ''.join( buf )
        command="select * from wubi where id ='%s'" % patten

        words= self.cache.get( patten )
    
        if  words:
            return words

        self.cu.execute(command)

        result = self.cu.fetchone()

        if result != None:
            words =result[1].split(',')
            self.cache[ patten ] = words
        else:
            words = []



        return words


class Wubi( Base_Key_Fsm):
    def Enter(self):
        del self.buffer[:]
        self.pmenu.check_omnifunc( )

    def Leave(self):
        self.pmenu.setback( )


    def __init__(self):
        super(Wubi, self).__init__()
        self.buffer=[]
        self.search=  _wubi_seach( )

        self.pmenu= pyvim.pmenu( )
        self.pmenu.set_omnifunc( 'input_monitor#OmniComplete' )


        


    def in_fsm( self, key):
        self.key= key

        callback=self.key_map.get(key, self.punc)
        callback()

    def wubi(self):
        self.match_words  = self.result( self.search.search(self.buffer) ) 

        imrc.wubi_match_words= self.match_words



    def result(self, words):
        '组成vim 智能补全要求的形式，这一步只是py形式的数据，vim要求是vim的形式'

        items=[{"word": " " ,"abbr":"%s        Wubi" %  ''.join(self.buffer) }]

        if len( self.buffer ) > 4:
            return items

        for i,w in enumerate(words):
            items.append({"word":w, "abbr":"%s.%s"%(i+1, w)})

        return items



    def backspace(self):
        if not pyvim.pumvisible():
            pyvim.feedkeys('\<bs>', 'n')
            return 0

        if len( self.buffer ) > 1:
            self.buffer.pop()
            self.wubi()
            self.pmenu.show( )
        else:
            del self.buffer[:]
            self.pmenu.cencel( )

   
    def enter(self):
        if pyvim.pumvisible():
            pyvim.feedkeys(r'%s\<C-e>' % ''.join(self.buffer),'n')
            del self.buffer[ : ]
            return 0
        pyvim.feedkeys(r'\<cr>' ,'n')

    def digit( self ):
        if pyvim.pumvisible():

            del self.buffer[:]
            self.pmenu.select( int(self.key) )
            return 0
        pyvim.feedkeys( self.key ,'n')


    def upper_letter( self ):
        del self.buffer[:]
        pyvim.feedkeys( self.key  ,'n' )


    def punc(self):
        callback=self.punc_map.get(self.key, None)

        if callback:
            callback()

    def lower_letter( self ):
        self.buffer.append( self.key )

        self.wubi()
        self.pmenu.show( )

    def space(self):
        del self.buffer[:]
        if pyvim.pumvisible():
            self.pmenu.select( 1 )
            return 0
        pyvim.feedkeys('\<space>', 'n')

    def esc( self ):
        del self.buffer[:]
        pyvim.feedkeys( '\<esc>','n')

        





class _key_fsm:
    def __init__( self ):
        self.base_key_fsm= Base_Key_Fsm( )
        self.base_code_fsm =Base_Code_Fsm()
        self.wubi_fsm=Wubi()



if not __name__=="__main__":
    key_fsm=_key_fsm()

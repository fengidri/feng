#encoding:utf8
import pyvim
import vim
import imrc
from im.base_context_fsm import Base_Context_Fsm


class Input_Monitor(object):
    def __init__( self ):
        self.context_fsm=Base_Context_Fsm( )
        self.pmenu= pyvim.pmenu( )
        self.pmenu.set_omnifunc( 'youcompleteme#OmniComplete' )
        self.context_switch= True
        self.mode = ''

    def filetype( self ):
        self.pmenu.clear( )
        filetype= vim.eval( '&ft' )
        if filetype == '':
            return 0
        if filetype == "c" or filetype == "cpp":
            #self.pmenu.set_omnifunc( 'ClangComplete' )
            self.pmenu.set_omnifunc( 'youcompleteme#OmniComplete' )

        if filetype == "python":
        #    self.pmenu.set_omnifunc( 'jedi#completions' )
            self.pmenu.set_omnifunc( 'youcompleteme#OmniComplete' )
        try:
            self.ft =__import__( 'im.ft.%s' % filetype ,globals(), locals(),['setting'])
            self.ft.setting( self ).setting( )
        except ImportError, e:
            pass
        #if filetype == 'python':
        #    self.pmenu.set_omnifunc( 'jedi#completions')

    def context( self ):
        if "1" == vim.eval( "g:im_just_wubi" ):
            return 'wubi', False
        complete_bool = True
        syntax_area =pyvim.syntax_area()
        if imrc.mode == 'muti_change':
            context = 'muti_change'
            return context, complete_bool

        if syntax_area in ['Constant', 'Comment','String']:

            if imrc.wubi_switch:
                context = 'wubi'
                complete_bool = False

                #如果光标之前的是字母,就进入code模式
                try:
                    char = pyvim.str_before_cursor()[ -1 ]
                    if char.islower( ) or \
                            char.isupper( ):
                        context='code'
                except Exception, e:
                    print e
                    pass
            else:
                context = syntax_area
        else:
            context = syntax_area
        return context, complete_bool

    def in_key( self, key ):
        if self.context_switch:
            context, complete_bool  = self.context( )


        self.context_fsm.in_fsm( context , key)
        if complete_bool:
            self.complete( key )


    def complete( self, key ):

        if (len(key) == 1)and(key.islower( ) or key.isupper( ) or key== '.' or
                key =='_'):
            self.pmenu.show( )

    def all_key( self ):
        "返回被监控的所有的键的list"
        return self.context_fsm.all_key( )

    def init_monitor_keys( self ):
        keys=self.all_key()
        for key in keys:
            if len( key ) > 1 and key.islower():
                map_key = '<%s>' % key
            else:
                map_key = key
            if key == '"':
                key = r'\"'
                map_key = '"'
            command='inoremap <expr> %s input_monitor#Input_Monitor( "%s" )' % ( map_key, key)
            vim.command(command)
    def muti_change_start( self ):
        self.mode = 'muti_change'


        
        





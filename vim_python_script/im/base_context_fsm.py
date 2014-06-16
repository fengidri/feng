#encoding:utf8
from base_key_fsm import key_fsm
class Base_Context_Fsm( object ):
    def __init__(self):
        self.context_map={ 
            'Constant':   key_fsm.base_key_fsm,
            'Comment':    key_fsm.base_key_fsm,
            'String':     key_fsm.base_key_fsm,
            'wubi':       key_fsm.wubi_fsm
            }
        self.default_fsm = key_fsm.base_code_fsm
        self.context='DEFAULT_CONTEXT'
        self.fsm=key_fsm.base_key_fsm
    
    def in_fsm( self, context, key):
        '当在多个key fsm之间进行切换时，在切入与切出时，可能要执行一些动作'
        '在基础状态机中有Enter Leave函数分应这两种情况'
        if self.context != context:
            print 'context:',context

            self.context = context

            self.fsm.Leave()
            self.fsm = self.context_map.get(context, self.default_fsm)
            self.fsm.Enter()

        self.fsm.in_fsm(key)

    def change_fsm(self, context, fsm):
        self.context_map[context] = fsm

    def change_default_fsm(self, fsm):
        self.default_fsm = fsm
    def set_default_fsm_wubi( self ):
        self.default_fsm = key_fsm.wubi_fsm

    def all_key( self ):
        return self.fsm.all_key( )
        



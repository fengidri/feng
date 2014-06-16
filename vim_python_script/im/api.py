#encoding:utf8
"""用户的设置,继承本类,并设置函数setting,在函数中调用API,
 本类的self.im是指向Input_Monitor,以参数的形式传进来可以很方便,不用import相关的
 模块,并且用户是不可见的.
"""
class ImApi( object ):
    def __init__( self, im):
        self.im=im
    def just_wubi( self ):
        self.im.context=self.wubi_context
    def wubi_context( self ):
        return 'wubi', False

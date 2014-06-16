#encoding:utf8
from im.api import ImApi
"""context在的设置文件"""
class setting( ImApi ):
    def setting( self ):
        "设置默认是wubi输入"
        self.just_wubi( )

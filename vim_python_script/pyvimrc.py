#encoding:utf8
#工程
#数据分成两种：
#  程序运行配置数据
#  用户相关数据
#对于程序运行数据在pyvimrc中设置
#对于用户相关数据在sqlite3数据文件中设置

import os
import sys
#sys.path.insert( 0, os.environ["PYTHONPATH"] )
sys.path.insert( 0, '/home/feng/Dropbox/root/lib/python')
Rootpath=''
comp_debug_conf = os.path.join( os.environ["HOME"] , '.scir_conf') 
favorite_dir = [os.environ["HOME"] + '/.projects']
user_db_file=os.environ["HOME"] + '/.user_db_file.sqlite'
user_json_file=os.environ[ "HOME" ] + '/.vim/user_data.json'

author = '丁雪峰'
email = 'fengidri@yeah.net'
phone='18575615848'




files = [
        '.vim/plugin/SmartInput/pyvimrc.py'
        ]



Project = [ 
{ "name":"CA UC 1.05",           "path":"/home/src/ca/ca/ca_UC1.05_tag8843/ca",    "kind": 0},
{ "name":"CA UC 1.04",           "path":"/home/src/ca/ca/ca_UC1.04_tag6897/ca",    "kind": 0},
{ "name":"CA UC trunk",          "path":"/home/src/ca/ca/ca_trunk/ca/",            "kind": 0},
{ "name":"CA UC ruiju",          "path":"/home/src/ca/ca/ruiju_ca/ca/",            "kind": 0},
{ "name":"FaxServer UC 1.05", "path":"/home/src/faxserver/uc_1.05_tag8984/src", "kind": 0},
{ "name":"FaxServer trunk",   "path":"/home/src/faxserver/trunk/src",           "kind": 0},
{ "name":"B2bua UC1.06",      "path":"/home/src/b2bua/mtc/release_UC_V1.06/", "kind": 0},
{ "name":"youcomplete",       "path":"/home/feng/.vim/bundle/YouCompleteMe/", "kind": 0},
{ "name":"System New",        "path":"/home/src/system/system-uc1.05/Code/", "kind": 'man'},
{ "name":"SipTk",             "path":"/home/src/SipTK", "kind": 'man'},
{ "name":"Approute",             "path":"/home/src/approute/uc_1.06_tag9999/",                         "kind": 0},
        ]

"""this is for the lang info"""
class _lang:
    pass
lang = _lang( )
lang.exegesis_sign=''
lang.exegesis_start=''
lang.exegesis_stop=''


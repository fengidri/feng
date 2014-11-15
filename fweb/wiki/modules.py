# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2014-11-14 23:48:24
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

import cPickle as pickle
import os
import logging
import time
WIKIPATH=''

__CLASS = {} # class: id, id, id
__TAGS = [] # tag, tag,
__INDEX = {}# id: title, tags, ctime, mtime, public
class Info(object):
    def __init__(self, Id, info):
        self.title = info[0]
        self.tags = info[1]
        self.ctime = info[2]
        self.mtime = info[3]
        self.public = info[4]
        self.Id = Id

    def read(self, name=''):
        return read(self.Id, name)

    def listdir(self):
        return listdir(self.Id)



indexfile = os.path.join(WIKIPATH, 'wiki.pickle')
def init():
    "初始化"
    global __INDEX
    global __TAGS
    global __CLASS
    if os.path.isfile(indexfile):
        __INDEX, __CLASS, __TAGS = pickle.load(open(indexfile,'r'))
    else:
        __INDEX = {}
        __CLASS = {}
        __TAGS = []

def save():
    pickle.dump((__INDEX, __CLASS, __TAGS), open(indexfile,'w'))

def get(Id):
    info = __INDEX.get(Id)
    if info:
        return Info(Id, info)
    return None

# 返回所有的文件的id
def list(order=''):
    if not order:
        return __INDEX.keys()
    elif order == 'mtime':
        tt = [(Id, v[3]) for Id,v in __INDEX.items()]
        return [t[0] for t in sorted(tt, key=tt[1])]
    elif order == 'ctime':
        tt = [(Id, v[2]) for Id,v in __INDEX.items()]
        return [t[0] for t in sorted(tt, key=tt[1])]

#返回所有的tag
def get_tags():
    return __TAGS


#增加一个新文章
#返回文件的id
def add(title, filename, content, cls='', tags=[], public=0):
    ctime = mtime = time.time()
    Id = int(time.time()) - 1416010575
    if Id in __INDEX:
        logging.error('%s dupile ' % Id)
        return -1#duplie ID
    dirpath = os.path.join(WIKIPATH, str(Id))
    if os.path.isdir(dirpath):
        logging.error('%s dupile ' % dirpath)
        return -2#duplie path

    for t in tags:
        if t not in __TAGS:
            __TAGS.append(t)
    clsadd(cls, Id)
    try:
        os.mkdir(dirpath)
    except:
        logging.error('%s mkdir %s fail')
        return -3
    fp = os.path.join(dirpath, filename)
    open(fp, 'w').write(content)
    __INDEX[Id] = [title, tags, ctime, mtime, public]
    return Id


# 把id 增加到对应的分类中
def clsadd(cls, Id):
    c = __CLASS.get(cls)
    if not c:
        __CLASS[cls] = [Id]
    else:
        c.append(Id)

# 设置一个id 对应的tag
def settag(Id, tag):
    info = __INDEX[Id]
    if not info:
        return -1
    for t in tags:
        if t not in __TAGS:
            __TAGS.append(t)
    info[1] = tag

# 设置发布的状态
def setpublic(Id, public):
    info = __INDEX[Id]
    if not info:
        return -1
    info[4] =public

#写入id下的文件
def write(id, name, context):
    info = __INDEX[id]
    if not info:
        return -1
    info[3] = time.time()
    dirpath = os.path.join(WIKIPATH, id)
    fp = os.path.join(dirpath, name)
    if not os.path.isdir(dirpath):
        try:
            os.mkdir(dirpath)
        except:
            logging.error('mkdir %s fail' % dirpath)
    open(fp, 'w').write(context)

# 文件对象下的所有的文件
def listdir(id):
    dirpath = os.path.join(WIKIPATH, id)
    if not os.path.isdir(dirpath):
        logging.error('%s not dir' % dirpath)
        return []
    return os.listdir(dirpath)

# 读取一个id对应的文件, 如果没有指定name, 就读取index
def read(id, name=''):
    dirpath = os.path.join(WIKIPATH, id)
    if not os.path.isdir(dirpath):
        logging.error('%s not dir' % dirpath)
        return None
    if not name:
        for f in os.listdir(dirpath):
            if f.startswith('index'):
                name = f
                break
        else:
            return None
    fp = os.path.join(dirpath, name)

    return open(fp).read()












    

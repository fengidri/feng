# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-03-15 17:53:13
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
# TODO 不支持 $$
import codecs

import logging


from words import split
from node import node_tree

class Config(object):
    ScanWords = False
    NodesList = False


# 1. 使用split 函数把source 分成多个Word对象, 所有的Word 实例组成Words 实例
# 2. 依赖于Words 中的Word.type 创建node. 这些node 组成node_tree






################################################################################
# 完成词法分析, 下面的代码实现语法分析, 生成多个语法树
################################################################################


#logging.basicConfig(level = logging.DEBUG)
def open_source_to_words(f):
    f = codecs.open(f, 'r','utf8')
    return split(f.read())

def savehtml(o, words):
    f = codecs.open(o, 'w','utf8')
    f.write(node_tree(words).html())


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i")
    parser.add_argument("-o")


    args = parser.parse_args()
    savehtml(args.o, open_source_to_words(args.i))


if __name__ == "__main__":
    main()
    pass


# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-03-15 17:51:59
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
class LostParamsEx(Exception):
    def __init__(self, word):
        print "%s:%s Lost Param" % (word.pos[0], word.pos[1])


if __name__ == "__main__":
    pass


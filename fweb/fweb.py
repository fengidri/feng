# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2014-11-15 20:26:30
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

import web
from wiki import wiki
from wiki.wiki import *
urls = (
    '/wiki/chapters', 'chapters',
    '/wiki/chapters/(\d+)', 'chapter',
        )

if __name__ == "__main__":
    app = application(urls, globals(), autoreload=True)
    app.run()

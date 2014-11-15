# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2014-11-14 22:05:50
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
import web
from web.contrib.template import render_jinja
from web.
import os
import json
urls = (
    '/wiki/chapters', 'chapters',
    '/wiki/chapters/(\d+)', 'chapter',
        )
import wiki.modules as dw#data of wiki

render = render_jinja(
        'templates',   # 设置模板路径.
        encoding = 'utf-8', # 编码.
    )

class chapters(object):
    def POST(self, Data):
        title = Data.get('title')
        filename = Data.get('filename')
        content = Data.get('content')
        return dw.add(title, filename, content)

        return title
    def GET(self, Date):#返回列表
        r = web.ctx.env.get('HTTP_RANGE','bytes=0-100')
        return dw.list()

class chapter(object):
    def GET(self, da, Id):
        Id = int(Id)
        chapter = dw.get(Id)
        if not chapter:
            raise web.NotFound()

        c = web.ctx.env.get('HTTP_ACCEPT', 'text/html')
        for tt in c.split(';'):
            kv = tt.split('=')
            if len(kv) == 2:
                k,v = kv
                k = k.strip()
                v = v.strip()
                if k == 'filename':
                    f= v
                    break
        else:
            f = ''
        if c.find('text/json+mkiv') > -1: 
            return {'name':chapter.title, 'context': chapter.read(f)}
        else:
            return render.wiki.html(chapter.read(f))
    def PUT(self, da, id):
        pass
class application(web.application):
    def handle(self):
        fn, args = self._match(self.mapping, web.ctx.path)
        if args:
            args.insert(0, web.input())
        else:
            args = [web.input()]
        res =  self._delegate(fn, self.fvars, args)
        if not isinstance(res, basestring):
            res = json.dumps(res)
        return res

if __name__ == "__main__":
    dw.WIKIPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
            'store')
    dw.init()
    app = application(urls, globals(), autoreload=True)
    app.run()

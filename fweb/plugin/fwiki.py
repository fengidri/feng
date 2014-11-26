# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2014-11-14 22:05:50
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
import os
import context
from cottle import static_file
import wiki.modules as dw       #data of wiki

STOREPATH = os.path.join(os.getcwd(), 'fengidri.github.io/store')
WIKIPATH = os.path.join(os.getcwd(), 'fengidri.github.io')
dw.init(STOREPATH)

name = 'fwiki'
urls = (
    '/chapters', 'chapters',
    '/chapters/(\d+)', 'chapter',
    '/(.*)', 'index',
        )

class index:# 提供静态网页功能
    def GET(self, filename):
        return static_file(filename, WIKIPATH)


class chapters(object):
    def POST(self):
        Data = self.forms
        title = Data.get('title')
        content = Data.get('content')
        cls = Data.get('class', '')
        res = dw.add(title,  content, cls = cls)
        dw.save()
        return res

    def GET(self):#返回列表
        c = self.env.get('HTTP_ACCEPT', 'text/html')
        ll = dw.list()
        if c.find('json') > -1:
            return ll
        else:
            file_list = []
            total_nu = len(ll)
            for index in ll:
                c = dw.get(index)
                file_list.append((c.title, index))
                
            return self.template("wiki_index", locals())

class chapter(object):
    def GET(self,  Id):
        Id = int(Id)
        chapter = dw.get(Id)
        if not chapter:
            self.abort(404)

        c = self.env.get('HTTP_ACCEPT', 'text/html')
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
            if not f:
                f = 'index.mkiv'
            f = chapter.read(f)
            if not f:
                self.abort(404)
            return {'name':chapter.title, 'content': f[1], 'filename':f[0],
                    'ID': Id}
        else:
            w = context.context2htmls(chapter.read(f)[1].decode('utf8'))
            return self.template("show_wiki", wiki= w, 
                    title =chapter.title, ID=Id)

    def PUT(self,  Id):
        Id = int(Id)
        chapter = dw.get(Id)
        if not chapter:
            self.abort(404)

        title = self.forms.get('title')
        content = self.forms.get('content')
        cls = self.forms.get('cls')
        chapter.settitle(title)

        chapter.write('index.mkiv',  content)
        dw.save()
        return Id
    def DELETE(self, Id):
        ID = dw.delete(int(Id))
        if not ID:
            self.abort(404)
        dw.save()
        return ID


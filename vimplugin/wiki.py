# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2014-11-17 17:00:06
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

import pyvim
import vim
import json
import urllib2
import tempfile
ID = None
SERVER="localhost"
class WikiPost(pyvim.command):
    def run(self):
        title, c = content()

        global ID
        if ID:
            print "ID %s. Should WikiPut" % ID 
            ID =  put(title, c)
        else:
            ID = post(title, c)
        ID = int(ID) 
        print ID

class WikiPut(pyvim.command):
    def run(self):
        global ID
        if not ID:
            print "not ID. Should WikiPost" 
            return 
        try:
            title, c = content()
        except:
            return

        ID =  put(title, c)
        ID = int(ID) 
        print ID

class WikiGet(pyvim.command):
    def run(self):
        global ID
        if not self.params:
            print "should input the ID of the cachpter"
            return
        _ID = self.params[0]
        tmp = get(_ID)
        if not tmp:
            return
        ID = _ID
        vim.command("edit %s" % tmp)


def content():
        title = ''
        for line in vim.current.buffer:
            if line.startswith('%%') or line[0] != '%':
                if not title:
                    print "not find title"
                    return
                break

            if line.startswith('%') and line.find('title')>-1:
                title = line.split(':')[-1].strip()
        if not title:
            print "not find title"
            return
        content = '\n'.join(vim.current.buffer)
        return (title, content)
def get(ID):
    url = 'http://%s/fwiki/chapters/%s' % (SERVER, ID)
    req = urllib2.Request(url)
    req.add_header('Accept', "text/json+mkiv")
    tmp = tempfile.mktemp()
    try:
        res = urllib2.urlopen(req).read()
    except Exception, e:
        print e
        return
    c = json.loads(res).get('content')
    if not c:
        print "not content"
        return 
    open(tmp, 'w').write(c)
    return tmp



def post(title, content):
    j = {'title':title, 'content': content}
    url = 'http://%s/fwiki/chapters' % SERVER
    req = urllib2.Request(url, json.dumps(j));

    req.add_header('Content-Type', "application/json");
    return urllib2.urlopen(req).read()

def put(title, content):
    if not ID:
        return
    j = {'title':title, 'content': content}
    url = 'http://%s/fwiki/chapters/%s' % (SERVER, ID)

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, json.dumps(j));

    request.add_header('Content-Type', 'application/json')
    request.add_header('Accept', 'application/json')
    request.get_method = lambda: 'PUT'
    return opener.open(request).read().strip()














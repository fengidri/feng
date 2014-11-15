# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2014-10-21 19:06:15
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

import web
import mescin
import json
import os
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
temp = web.template.render("static/tpl")

class VuiIndex(object):
    def GET(self):
        return temp.vuiprojects()

class VuiProjects(object):
    def GET(self):
        configs = mescin.ProConfigs()
        names = configs.get_names()
        return json.dumps(names)
class VuiProjectsContent(object):
    def GET(self, name):
        configs = mescin.ProConfigs()
        return json.dumps(configs.get_by_name(name)[0].json)



class UploadBase():
    def upload(self, flag, path, content):
        if flag == None:
            return web.internalerror("Bad, bad server. No donut for you.")
        else:
            flag = int(flag)

        path_tmp = path + "_tmp"

        if flag == 0:
            if os.path.isfile(path):
                return web.internalerror("Bad, bad server. No donut for you.")
            mode = "w"
        else:
            mode = "a"

        if content:
            f= open( path_tmp, mode )
            f.write(  content )
            f.close( )

        if flag == -1:
            os.rename(path_tmp, path)
            return True
        return False

class Uploadtest(UploadBase):
    share_dir = "/tmp/share"
    def GET(self):
        return temp.upload()
    def POST(self):
        filename   = web.input().get('filename')
        flag       = web.input().get('flag')
        content  = web.input().get('content')
        if content == None:
            content  = web.input(content = {}).content.value
        if content == None:
            return web.internalerror("Bad, bad server. No donut for you.")
            
    
        if not os.path.isdir(self.share_dir):
            os.mkdir(self.share_dir)
        path = os.path.join(self.share_dir, filename)
        if self.upload(flag, path, content):
            print web.input().get('svn_log')
            print web.input().get('svn_num')
            print web.input().get('svn_branch')
            print web.input().get('version')
            print web.input().get('name')
    
        #chmod = request.forms.get('chmod')
        return path




class Xclip(object):
    data = ""
    def GET(self, down=False):
        cli = os.popen("xclip -o").read()
        if down:
            web.ctx.headers.append(("Content-Disposition","attachment;filename=clip.txt"))
            return cli
        else:
            return temp.clip(cli, self.data)
    def POST(self):
        Xclip.data = web.input().get("tmp")
        raise web.seeother('/xclip')
class LocalGvim(object):
    def POST(self):
        arg = web.input().get('arg')
        os.popen2('gvim %s' % arg)
        return ''


urls = (
        "/vuiprojects/list", VuiProjects,
        "/vuiprojects/content/(.+)", VuiProjectsContent,
        "/vuiprojects", VuiIndex,
        "/xclip/(.*)", Xclip,
        "/xclip", Xclip,
        "/upload", Uploadtest,
        '/local/gvim', LocalGvim
        )


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()


        

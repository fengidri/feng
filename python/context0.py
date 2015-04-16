#encoding:utf8
# @     model: context.py              #
# @    author: feng/fengidri/feng_idri #
# @   version: 1.0.3                   #
# @ first_time: 2013-06-18 08:37:37    #
# @ last_time: 2013-06-18 08:37:58     #



import re
import  codecs


class context:
	'context class'
	def __init__(self,source):
		self.source=source
		self.content=[]
		self.title=''
		self.titletag=u'''<h1>%s</h1>\n'''
		self.contenttag=u'''<div id='h1_div'>\n%s\n</div>\n'''

		self.protect_typing()

		source=self.source
		#预处理
		#	source	=source.replace(u'\r\n',"\n")
		#	source	=source.replace(u'\r\n',"\n")
		#	source  =re.sub(ur'\r\n','\n',source)

		source  =re.sub(ur'([^\\]|)%.*\n',ur'\1\n',source)#正则空位
		source	=re.sub(ur'\n\s*\n\s*(\n\s*)*',ur'\\par\n',source)

		regex =ur'\\chapter\s*\{[^}]*\}'
		part_list = re.split(regex,source)
		part_title_list    =re.findall(regex,source)#直接写在这里.insert() 得到空
		part_title_list.insert(0,'')
		for i,part in enumerate(part_list):
			title=part_title_list[i]
			self.content.append(chapter(part,title))
	def html(self):
		self.html=''
		if self.title!='':
			self.html+=self.titletag% title
		content= u''.join([c.html() for c in self.content])
		self.html+=self.contenttag %(content)
		self.uprotect_typing()

		return self.html
	def protect_typing(self):
		regex=ur'\\starttyping[\s\S]*?\\stoptyping'#写在\\starttyping(.|\n)*\\stoptyping|\\startcode(.|\n)*\\stopcode p中间有一个None?
		#ur'\\starttyping(.|\n)*\\stoptyping'  分成三段了
		p    = re.split(regex,self.source)
		self.protect_list = re.findall(regex,self.source)
		self.source =  ur'\TyPiNgTyPiNgTyPiNg'.join(p)
	def uprotect_typing(self):
		regex=ur'\\TyPiNgTyPiNgTyPiNg'
		p= re.split(regex,self.html)
		html=p[0]
		if len(p) - len(self.protect_list) ==1:
			for i,protect in enumerate(self.protect_list):
				match=re.search(ur'\\starttyping([\s\S]*)\\stoptyping',protect)
				if match:
					html=html +'<pre>'  + match.group(1) +'</pre>'
					html+= p[i+1]
		else:
			pass
		self.html=html
class chapter(context):
	'chapter class'
	def __init__(self,source,title):
		self.content=[]#section
		self.title=title
		regex =ur'\\section\s*\{[^}]*\}'
		parts_list = re.split(regex,source)
		parts_title_list    =re.findall(regex,source)
		parts_title_list.insert(0,'')

		for i,part in enumerate(parts_list):
			title=parts_title_list[i]
			self.content.append(section(part,title))
	def html(self):
		match=re.search(ur'\\chapter\s*\{([^}]*)\}',self.title)
		self.html=''
		if match:
			title=match.group(1)
			self.html+='''<h2>%s</h2>\n''' %title
		content=''
		for c in self.content:
			content +=c.html()
		self.html += u'''\n<div id='chapter_h2_div'>\n %s \n</div> \n''' %(content)
		return self.html
class section(chapter):
	def __init__(self,source,title):
		self.content=[]#subsection
		self.title=title
		regex =ur'\\subsection\s*\{[^}]*\}'
		parts_list = re.split(regex,source)
		parts_title_list    =re.findall(regex,source)
		parts_title_list.insert(0,'')
		for i,part in enumerate(parts_list):
			title=parts_title_list[i]
			self.content.append(subsection(part,title))
	def html(self):
		match=re.search(ur'\\section\s*\{([^}]*)\}',self.title)
		self.html=''
		if match:
			title=match.group(1)
			self.html+='''<h3>%s</h3>\n''' %title
		content=''
		for c in self.content:
			content +=c.html()
		self.html +=u'''<div id='section_h3_div'>\n %s \n</div> \n''' %(content)
		return self.html
class subsection(section):
	def __init__(self,source,title):
		self.content=[]#subsection
		self.title=title
		regex =ur'\\subsubsection\s*\{[^}]*\}'
		parts_list = re.split(regex,source)
		parts_title_list    =re.findall(regex,source)
		parts_title_list.insert(0,'')
		for i,part in enumerate(parts_list):
			title=parts_title_list[i]
			self.content.append(subsubsection(part,title))
	def html(self):
		match=re.search(ur'\\subsection\s*\{([^}]*)\}',self.title)
		if match:
			title=match.group(1)
		else:
			title=''
		content=''
		for c in self.content:
			content +=c.html()
		return u'''\n<h4>%s</h4>\n<div id='subsection_h4_div'>\n %s \n</div> \n''' %(title,content)
class subsubsection(subsection):
	def __init__(self,source,title):
		self.content=[]#subsection
		self.title=title
		self.content=context_to_obj(source)
	def html(self):
		match=re.search(ur'\\subsubsection\s*\{([^}]*)\}',self.title)
		if match:
			title=match.group(1)
		else:
			title=''
		content=''
		for c in self.content:
			content +=c.html()
		return u'''\n<h5>%s</h5>\n<div id='subsubsection_h5_div'>\n %s \n</div> \n''' %(title,content)
class context_command:
	def __init__(self,source):
		self.source=source
	def is_obj(self):
		regex=self.regex
		self.match = re.search(regex, self.source)
		return self.match
	def get_return(self):
		self.parts_list    =re.split(self.regex, self.source, maxsplit=1)
		return self.parts_list
class par(context_command):
	#---
	regex=ur'\\par'
	def __init__(self,source):
		context_command.__init__(self,source)
	def is_obj(self):
		return context_command.is_obj(self)
	def get_return(self):
		return context_command.get_return(self)
	def html(self):
		#---
		return u'\n<p>\n'
class text(context_command):
	def __init__(self,source):
		self.source=source
	def get_return(self):
		return [self]
	def html(self):
		return self.source
class itemize(context_command):
	#---
	regex=ur'\\startitemize[\s\S]*?\\stopitemize'#有行不能配置????
	def __init__(self,source):
		context_command.__init__(self,source)
	def is_obj(self):
		return context_command.is_obj(self)
	def get_return(self):
		return context_command.get_return(self)
	def html(self):
		#---
		html = self.match.group(0)
#		html = html.replace(ur'\startitemize',r'<table>')
#		html = html.replace(ur'\stopitemize',r'</table>')
#		html = re.sub(ur'\\VL',ur'<td></td>',html)
#		html = re.sub(ur'\\NC',ur'<tr><td>',html)
#		html = re.sub(ur'\\AR',ur'</td></tr>',html)
		html = html.replace(ur'\startitemize',r'<ul><li>')
		html = html.replace(ur'\stopitemize',r'</li></ul>')
		html = html.replace(ur'\item',r'</li><li>')
		html = re.sub(ur'<li>[\s\n]*</li>',r'',html)
		return html
def context_to_obj(source):
	class_list =[par,itemize]
	for p in class_list:
		obj = p( source)
		if obj.is_obj( ):
			parts_list= obj.get_return()
			return context_to_obj(parts_list[0])+[obj]+context_to_obj(parts_list[1])
			break
	return text(source).get_return()

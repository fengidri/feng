# -*- coding: utf-8 -*-
'''
发送html文本邮件
'''
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart
import email
import sys
  
class Post:
    def set_filetype(self, tp):#生成可加附件的对象
        if tp == "attached":
            self.main_msg = email.MIMEMultipart.MIMEMultipart()
    def set_attached_from_stdin(self):#从标准输入读取文字流
        contype = 'application/octet-stream'  
        maintype, subtype = contype.split('/', 1)  

        file_msg = email.MIMEBase.MIMEBase(maintype, subtype)  

        file_msg.set_payload(sys.stdin.read())
        email.Encoders.encode_base64(file_msg)
        file_msg.add_header('Content-Disposition','attachment', filename = "postoffice.txt")
        self.main_msg.attach(file_msg)
    def addtextmsg( self, msg ):
        self.main_msg = MIMEText( msg, "html", "utf-8" )
    def set_to_info(self, to_email):
        self.main_msg['To'] = to_email
        self.To = to_email
    def set_from_info(self, user, password):
        self.User = user
        self.Password = password
    def set_host(self, host):
        self.Host = host
    def set_subject(self, subject):
        self.main_msg["Subject"] = subject

    def send_mail(self):
        print self.main_msg.as_string()
        return 0

        try:  
            s = smtplib.SMTP()
            s.connect(self.Host)  #连接smtp服务器
            s.login(self.User, self.Password)  #登陆服务器
            s.sendmail('PostOffice<%s>'  % self.User, 
                    self.To, 
                    self.main_msg.as_string())  #发送邮件
            s.close()  
            return True  
        except Exception, e:  
            print str(e)  
            return False  
if __name__ == "__main__":
    post = Post()
    post.set_filetype("attached")
    post.set_host("HOST")
    post.set_to_info("TO")
    post.set_from_info("FROM", "PASSWORD")
    post.set_attached_from_stdin()
    post.set_subject("SUBJECT")
    post.send_mail()
    

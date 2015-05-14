# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-05-11 17:24:26
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
from imapclient import IMAPClient

import email
import email.header
from email.header import decode_header

import pynotify
import time
import logging
import traceback
import base64
import re
import os
import sys
import traceback

GMAIL_URL     = 'https://mail.google.com/mail/u/%s'
GMAIL_MSG_URL = '%s/#all/%%s'



# 在subject 中可能会出现多段编码的内容. 所以要对于email.header.ecre 进行修改
email.header.ecre = re.compile(r'''
  =\?                   # literal =?
  (?P<charset>[^?]*?)   # non-greedy up to the next ? is the charset
  \?                    # literal ?
  (?P<encoding>[qb])    # either a "q" or a "b", case insensitive
  \?                    # literal ?
  (?P<encoded>.*?)      # non-greedy up to the next ?= is the encoded string
  \?=                   # literal ?=
#  (?=[ \t]|$)           # whitespace or the end of the string
  ''', re.VERBOSE | re.IGNORECASE | re.MULTILINE)

class Emsg(object):
    def decode(self, h):
        _h = u''
        for m, charset in decode_header(h):
            if charset == None:
                _h += m
            else:
                _h += m.decode(charset)
        return _h

    def __init__(self, msg):
        self.msg = email.message_from_string(msg)

    def _addrs(self, addrs):
        addrlist = []
        regex = "(^.*)<(.*)>"
        for addr in addrs.split(','):
            addr = addr.strip()
            addr = re.sub('\r?\n', ' ', addr)
            match = re.search(regex, addr)
            if not match:
                addrlist.append((addr.split('@')[0], addr))
            else:
                name = self.decode(match.group(1))
                addr = match.group(2)
                addrlist.append((name, addr))
        return addrlist

    def Header(self, field):
        return self.msg[field]

    @property
    def Subject(self):
        return self.decode(self.msg['Subject'])

    @property
    def To(self):
        return self._addrs(self.msg['To'])

    @property
    def From(self):
        return self._addrs(self.msg['From'])

    @property
    def Cc(self):
        if cc == self.msg['Cc']:
            return self._addrs(cc)
        else:
            return []

    @property
    def Date(self):
        d = self.msg['Date']
        if not d:
            d = self.msg['Received'].split(';')[-1].strip()

    @property
    def Date(self):
        d = self.msg['Date']
        if not d:
            d = self.msg['Received'].split(';')[-1].strip()

        return time.mktime(email.utils.parsedate(d))

def getunseen(cfg):
    CHECKED = cfg['CHECKED']

    imap = cfg.get("__client")
    if not imap:
        imap = IMAPClient(cfg["HOST"], cfg["PORT"], use_uid=True, ssl= True)
        imap.login(cfg["USER"], cfg["PWD"])
        cfg["__client"] = imap

    checks = []

    for attr, fa, folder in imap.list_folders():
        if '\\Noselect' in attr or folder.startswith('[Gmail]/'):
            continue

        imap.select_folder(folder, readonly = True)

        ids = []
        _ids = imap.search('UNSEEN')
        for i in _ids:
            if i in CHECKED:
                continue
            ids.append(i)

        checks += ids
        if len(ids) > 5 or len(checks) > 20:
            notify('Check', 'Too More Email', cfg["GMAIL_URL"])
            break

        for msg in imap.fetch(ids, ['RFC822.HEADER', 'X-GM-THRID']).values():
            thrid = hex(msg['X-GM-THRID'])[2:]#just for google
            MSG = Emsg(msg['RFC822.HEADER'])


            notify(MSG.From[0][0], MSG.Subject, cfg["GMAIL_MSG_URL"] % thrid)


    return checks

def config():
    cfg = {}
    regex = "^GMAIL_(\d+)_(.*)$"
    for k, v in os.environ.items():
        match = re.search(regex, k)
        if not match:
            continue

        index = match.group(1)
        _k = match.group(2)

        cf = cfg.get(index)
        if not cfg:
            cfg[index] = {}
            cf = cfg.get(index)
        cf[_k] = v

    configs = []

    need_del = []
    for index , cf in cfg.items():
        if not cf.get("USER") or  not cf.get("PWD"):
            need_del.append(index)
            continue

        if not cf.get("HOST"):
            cf["HOST"] = 'imap.gmail.com'

        if not cf.get("PORT"):
            cf["PORT"] = 993
        cf["CHECKED"] = []
        cf["GMAIL_URL"] = GMAIL_URL % index
        cf["GMAIL_MSG_URL"] = GMAIL_MSG_URL %(cf["GMAIL_URL"])
    for i in need_del:
        del cfg[i]

    return cfg

def notify(efrom, msg, href):
    pynotify.init('Email')
    msg = "%s:  <a href='%s' >%s</a>" % ( efrom, href, msg)
    notice = pynotify.Notification('Email', msg)
    notice.show()


def main():
    cfgs = config()

    for cfg in cfgs.values():
        print 'Check: %s' % cfg['USER']

    while True:
        for cfg in cfgs.values():
            try:
                cfg["CHECKED"] += getunseen(cfg)
            except Exception, e:
                traceback.print_exc()

        logging.info('check over')
        time.sleep(60 * 4)



if __name__ == "__main__":
    main()


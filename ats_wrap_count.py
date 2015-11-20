# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-11-17 07:22:55
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

TMPDIR = '/tmp'
LOGFILE = '/tmp/log'
ATSROOTS = ['/usr/local/ats_422', '/usr/local/ats_ssd_422']

import os
import time
def getbs(filename):
    fd= os.open(filename, os.O_RDONLY)
    try:
        t = os.lseek(fd, 0, os.SEEK_END)
        os.lseek(fd, t/2, os.SEEK_SET)
        return os.read(fd, 512)
    finally:
        os.close(fd)


def _check(filename):
    bs = getbs(filename)
    if not bs:
        return

    dd_filename = os.path.join(TMPDIR, 'wrap_' + filename.replace('/', '_'))
    bs_old = None
    if os.path.exists(dd_filename):
        bs_old = open(dd_filename).read()

    if bs == bs_old:
        return 0

    open(dd_filename, 'w').write(bs)
    return 1



def check(fs):
    t = time.asctime(time.localtime(time.time()))
    log = open(LOGFILE, 'a')
    for f in fs:
        tt = _check(f)
        if tt != None:
            log.write("[%s] disk: %s status: %s\n" % (t, f, tt))

def getdisks(atsroot):
    disks = []
    for r in atsroot:
        sc = os.path.join(r, 'etc/trafficserver/storage.config')
        if os.path.exists(sc):
            for line in open(sc).readlines():
                line = line.split()[0]
                line = line.strip()
                if line[0] == '#' or len(line) < 5:
                    continue
                if not line.startswith('/dev/'):
                    line = os.path.join(line, 'cache.db')
                if not os.path.exists(line):
                    continue
                disks.append(line)
    return disks


check(getdisks(ATSROOTS))




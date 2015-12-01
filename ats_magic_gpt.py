#!/usr/bin/python
# -*- coding:utf-8 -*-
#    author    :   fengidri
#    time      :   2015-11-17 07:22:55
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

import sys
import struct
import os

BLOCK_SIZE = 8192
ATS_SKIP = 8192

import fcntl
import os
import struct
import array
import sys

BLKGETSIZE=0x1260
BLKGETSIZE64=0x80081272
BLKSSZGET=0x1268
BLKPBSZGET=0x127b

def ioctl_sector_size(fd):
    buf = array.array('c', [chr(0)] * 4)
    fcntl.ioctl(fd, BLKSSZGET, buf)
    return struct.unpack('I',buf)[0]

def size(s):
    s = float(s)
    PS = 'KMGT'
    for p in PS:
        s = s/1024
        if s < 1024:
            break
    return "%.3f%s" % (s, p)

def head(disk):
    """
          unsigned int magic;
          unsigned int num_volumes;            /* number of discrete volumes (DiskVol) */
          unsigned int num_free;               /* number of disk volume blocks free */
          unsigned int num_used;               /* number of disk volume blocks in use */
          unsigned int num_diskvol_blks;       /* number of disk volume blocks */
          uint64_t num_blocks;
    """
    fmt = "@5I1Q"

    f = open(disk, 'rb')
    f.seek(ATS_SKIP)
    data = f.read(struct.calcsize(fmt))
    f.close()

    return struct.unpack(fmt, data)



def checkmagic(disks):
    for i in disks:
        if not os.path.exists(i):
            continue
        try:
            m, nv, nf, nu, nd, nb =   head(i)
        except IOError, e:
            print i, e
            continue

        print "%s: " % i,
        if m == 0xabcd1237:
            print "\033[31mOK ^_^\033[0m",
        else:
            print "\033[31mFail @_@\033[0m",

        print hex(m), nb, size((nb + 1) * BLOCK_SIZE)


def _rmgpt(disk, do):
    f = open(disk, 'rb')
    sector_size = ioctl_sector_size(f)

    f.seek(sector_size)
    fmagic = f.read(8)

    f.seek(sector_size * -1, os.SEEK_END)
    bmagic = f.read(8)

    f.close()

    if fmagic == 'EFI PART' or bmagic == 'EFI PART':
        print "\033[31m%s is GPT.\033[0m" % disk

        if do:
            print "\033[31mDelete GPT ........\033[0m"
            f = open(disk, 'wb')

            f.write('\0' * ATS_SKIP) # clear all data before  ats

            f.seek(sector_size * -1, os.SEEK_END)
            f.write('\0' * sector_size) # clear all data before  ats

            f.close()

        return True
    else:
        print "%s is not GPT." % disk
    return False

def rmgpt(disks, do):
    if not do:
        print "Just Check. Not Change the disk."
        print "================================================"

    checkmagic(disks)
    print "================================================"

    count = 0
    for disk in disks:
        try:
            if _rmgpt(disk, do):
                count += 1
                checkmagic([disk])
        except IOError, e:
            print disk, e

        print ""
    return count

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
                if not line.startswith('/dev/') or line[-1].isdigit():
                    #line = os.path.join(line, 'cache.db')
                    continue
                if not os.path.exists(line):
                    continue
                disks.append(line)
    return disks

def main():
    args = sys.argv
    if len(args) < 2:
        print "ats.py [magic|rmgpt] <disks>"
        return

    sub = args[1]

    if sub == 'magic':
        checkmagic(args[2:])

    elif sub == 'rmgpt':
        do = False
        if len(args) == 3:
            if args[2] == 'YES':
                do = True

        rmgpt(getdisks(['/usr/local/ats_422']), do)

    elif sub == 'scan':
        stdou = sys.stdout
        sys.stdout = open('/dev/null', 'w')
        count = rmgpt(getdisks(['/usr/local/ats_422']), False)
        sys.stdout = stdou
        print count

    else:
        print "ats.py [magic|rmgpt] <disks>"


main()


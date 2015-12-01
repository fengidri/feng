# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-12-01 03:03:50
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
import sys
def sizefmt(s):
    s = float(s)
    PS = 'KMGT'
    for p in PS:
        s = s/1024
        if s < 1024:
            break
    return "%.3f%s" % (s, p)

class SmapsSec(object):
    def __init__(self, lines):
        line = lines[0].strip()
        tt = line.split(' ', 5)
        if len(tt) == 5:
            name = "anonymous"
        else:
            name = tt[-1].strip()

        self.line = line
        self.name = name

        _start, _end = tt[0].split('-')
        self.start = int(_start, 16)
        self.end = int(_end, 16)
        self.size= self.end - self.start

        self.rss = int(lines[2].split()[1]) * 1024


def parser_smaps(lines):
    assert(len(lines) % 16 == 0)
    n = len(lines)/16
    Secs = []

    for i in range(n):
        i = i * 16
        Secs.append(SmapsSec(lines[i: i + 16]))
    return Secs


def sum_smaps_handle(lines, S):
    secs = parser_smaps(lines)

    if S:
        secs = sorted(secs, key = lambda a : a.rss, reverse = False)

    sum_size = 0
    malloc_size = 0
    for sec in secs:
        sum_size += sec.rss
        print "%s %s %s" % (sizefmt(sec.rss).rjust(8),
                sizefmt(sec.size).rjust(8), sec.line)

        if sec.name == "anonymous" or sec.name == '[heap]':
            malloc_size += sec.rss

    print "Mem Usage Total: RSS: %d: %s" % (sum_size, sizefmt(sum_size))
    print "           Anonymous: %d: %s" % (malloc_size, sizefmt(malloc_size))




def origin(lines, S):
    show = []
    for line in lines:
        line = line.strip()
        tt = line.split(' ', 5)
        if len(tt) == 5:
            name = "anonymous"
        else:
            name = tt[-1]

        _start, _end = tt[0].split('-')
        size = int(_end, 16) - int(_start, 16)

        show.append((line, size))

    if S:
        show = sorted(show, key = lambda a : a[1], reverse = False)

    for k, v in show:
        print sizefmt(v).ljust(10), ' ', k



def main():
    handle = sum_smaps_handle
    filename = None
    sort = False
    for o in sys.argv[1:]:
        if o == '-o':
            handle = origin
            continue
        if o == '--sort':
            sort = True
            continue
        filename = o
    if not filename:
        return


    lines = open(filename).readlines()
    handle(lines, sort)


if __name__ == "__main__":
    main()



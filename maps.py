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
        line = lines[0]
        tt = line.split(' ', 5)
        if len(tt) == 5:
            name = "anonymous"
        else:
            name = tt[-1].strip()

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

    max_len = 0
    maps = {}
    for sec in secs:
        name = sec.name
        size = sec.rss

        if name in maps:
            maps[name] += size
        else:
            maps[name] = size

        if max_len < len(name):
            max_len = len(name)

    max_len += 4

    show = []
    for k, v in maps.items():
        show.append((k.ljust(max_len), v))

    if S:
        show = sorted(show, key = lambda a : a[1], reverse = False)

    sum_size = 0
    for k, v in show:
        print k, ': ', sizefmt(v)
        sum_size += v

    print "Mem Usage Total: %d: %s" % (sum_size, sizefmt(sum_size))


def sum_handle(lines, S):
    max_len = 0
    maps = {}
    for line in lines:
        tt = line.split(' ', 5)
        if len(tt) == 5:
            name = "anonymous"
        else:
            name = tt[-1].strip()

        _start, _end = tt[0].split('-')
        size = int(_end, 16) - int(_start, 16)

        if name in maps:
            maps[name] += size
        else:
            maps[name] = size

        if max_len < len(name):
            max_len = len(name)

    max_len += 4

    show = []
    for k, v in maps.items():
        show.append((k.ljust(max_len), v))

    if S:
        show = sorted(show, key = lambda a : a[1], reverse = False)

    sum_size = 0
    for k, v in show:
        print k, ': ', sizefmt(v)
        sum_size += v

    print "Mem Usage Total: %d: %s" % (sum_size, sizefmt(sum_size))


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
    sort = True
    for o in sys.argv[1:]:
        if o == '-o':
            handle = origin
            continue
        if o == '--no-sort':
            sort = False
            continue
        filename = o
    if not filename:
        return


    lines = open(filename).readlines()
    handle(lines, sort)


if __name__ == "__main__":
    main()



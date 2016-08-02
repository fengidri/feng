# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2016-08-02 03:07:55
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
import os
import time

cmd = "iptables -L -nvx  --line-numbers"

last_data = {}

def fmt(s):
    s = float(s)
    p = ' KMGTP'
    i = 0

    while s > 1024 and i < len(p):
        s = s / 1024
        i = i + 1

    return "%.f%s" % (s, p[i])


def output(t, l, d):
    if d == 'INPUT':
        d = '<'
    elif d == 'OUTPUT':
        d = '>'
    else:
        d = '-'

    value = int(t[2])

    speed = 0
    if l:
        speed = value - l

    t.insert(0, fmt(speed))
    t.insert(0, d)
    print ' '.join(t)

    return value


def speed():
    lines = os.popen(cmd).readlines()
    d = 'INPUT'

    for line in lines:
        line = line.strip()
        if not line:
            continue

        t = line.split()

        key = t[0]

        if not key.isdigit():
            if key == 'Chain':
                d = t[1]
            continue

        key = key + d

        last_value = last_data.get(key)
        last_data[key] = output(t, last_value, d)



def main():
    while 1:
        os.system('clear')
        speed()
        time.sleep(1)



main()


















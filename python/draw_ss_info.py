# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2016-04-12 13:05:00
#    email     :   fengidri@yeah.net
#    version   :   1.0.1





def parser(f):
    info = {}
    lines = open(f).readlines()
    for line in lines:
        if line.startswith('E'):
            continue
        if line.startswith('S'):
            continue
        line = line.strip()
        t = line.split()
        for tt in t:
            x = tt.split(':')
            try:
                float(x[1])
            except:
                continue
            if len(x) == 2 :
                if info.get(x[0]) == None:
                    info[x[0]] = [x[1]]
                else:
                    info[x[0]].append(float(x[1]))
    return info



import pylab

import numpy as np

import matplotlib.pyplot as plt
import sys

f1 = sys.argv[1]
f2 = sys.argv[2]


#t =  parser('fail_1.log')[k]
#plt.plot(range(0, len(t)), t)
#
fig, p = plt.subplots(1, 3)
for i, k in enumerate(['ssthresh', 'cwnd', 'rto', 'rtt']):
    sub = p[i]

    t = parser(f1)[k]
    sub.plot(range(0, len(t)), t, label = f1)

    t = parser(f2)[k]
    sub.plot(range(0, len(t)), t, label = f2)
    sub.legend()
    sub.set_title(k)

fig.set_size_inches(40, 10.5)

fig.savefig("/var/http/ss_info_.png" )


if __name__ == "__main__":
    pass



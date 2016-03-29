# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2016-01-13 02:12:39
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

flag1 = '<'
flag2 = '>'


import sys
import numpy as np
import matplotlib.pyplot as plt

class Xplot(object):
    def __init__(self, plt):
        self.color = 'k'
        self.plt = plt

    def read(self, f):
        seqs_y = []
        seqs_x = []

        acks_y  = []
        acks_x  = []

        wins_y  = []
        wins_x  = []

        for line in f.readlines():
            t = line.split()
            if t[0] == flag1:
                seqs_x.append(float(t[1]))
                seqs_y.append(int(t[2]))

            elif t[0] == flag2:
                acks_x.append(float(t[1]))
                acks_y.append(int(t[3]))

                wins_x.append(float(t[1]))
                wins_y.append(int(t[4]))

        self.plt.plot(seqs_x, seqs_y, 'rx-', linewidth=0.1,  markersize=0.2)
        self.plt.plot(acks_x, acks_y, 'gx-', linewidth=0.1,  markersize=0.2)
        self.plt.plot(wins_x, wins_y, 'bx-', linewidth=0.1,  markersize=0.2)

    def save(self, out):
        self.plt.savefig(out)


plt.figure(figsize=(50,30))
xplot = Xplot(plt)
xplot.read(open(sys.argv[1]))
xplot.save(sys.argv[2])

if __name__ == "__main__":
    pass



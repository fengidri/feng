# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2016-03-25 15:33:08
#    email     :   fengidri@yeah.net
#    version   :   1.0.1


import pylab

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
import sys
plt.rcParams['savefig.facecolor'] = "0.8"
plt.rc('xtick', labelsize='medium', direction='out')
plt.rc('ytick', labelsize='medium', direction='out')
plt.rc('xtick.major', size=8, pad=4)
plt.rc('xtick.minor', size=5, pad=4)
index = 0

def get_data(f):
    lines = open(f).readlines()
    data = []
    num = 0
    m = 0
    for line in lines:
        t = line.split()
        if t[1] == '200':
            num +=1
            tt = float(t[index])
            if m < tt:
                m = tt
            data.append(tt)
    print "%s: data number: %d max: %s" % (f, num, m)
    return data





infos = [ ('log_16', 'grey', '16k'),
        ('log_32', 'blue', '32k'),
        ('log_64', 'yellow', '64k'),
        ('log_128', 'white', '128k'),
        ('log_256', 'green', '256k'),
        ('log_512', 'black', '512k'),
        ('log_1024', 'red', '1024k'),

        ]

def draw(title):
    fig, p = plt.subplots(4, 2, sharex = True)
    i = 0
    for x in p:
        for xx in x:
            if i >= len(infos):
                break

            info = infos[i]
            i += 1
            xx.hist(get_data(info[0]), 90, facecolor=info[1], alpha=0.5, label = info[2])
            xx.legend(loc = 0)
            xx.xaxis.set_major_locator(MultipleLocator(0.5))
            xx.xaxis.set_minor_locator(MultipleLocator(0.1))
            xx.spines['right'].set_visible(False)
            xx.spines['top'].set_visible(False)
            xx.yaxis.set_ticks_position('left')
            xx.xaxis.set_ticks_position('bottom')

    xx.set_xlabel('Time/s')



    #ax1.set_title(sys.argv[2])


    #ax1.legend()
    fig.set_size_inches(20, 10.5)
    fig.tight_layout()
    fig.suptitle(title, fontsize = 30)
    fig.subplots_adjust(top=0.90)
    plt.savefig("/var/http/ats_%s.png" % title.lower().replace(' ', '_'))

index = 12
draw('Max Read Time')

index = 7
draw('First Byte Time')

index = 10
draw('Total Time')

if __name__ == "__main__":
    pass



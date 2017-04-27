# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2016-08-17 02:07:56
#    email     :   fengidri@yeah.net
#    version   :   1.0.1



import os
import sys
import json
import time

###### load data

def time_formatter(timestamp, pos):
    "show time hour and mins look like: HH:MM"
    timestamp += 8 * 3600

    return time.strftime("%H:%M", time.gmtime(timestamp))

#####################################################
opt_kv      = KV  # {'label':[x, y1, y2]}
opt_title   = "MG"
opt_xlabel  = "Time"
opt_y1label = "SlowRate"
opt_y2label = "User"
#####################################################
import matplotlib as mpl
mpl.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter


fig, axarr = plt.subplots(2, sharex=True)

ax1 = axarr[0]
ax2 = axarr[1]


lines = []

for label, kv in opt_kv.items():
    print label

    l, = ax1.plot(kv[0], kv[1], label = label)
    lines.append(l)

    ax2.plot(kv[0], kv[2])


plt.legend(lines, lines_label)


ax1.set_title(opt_title)
ax1.set_ylabel(opt_y1label)

ax2.set_xlabel(opt_xlabel)
ax2.set_ylabel(opt_y2label)
#plt.ylim(0, 30)

ax = plt.gca()
ax.xaxis.set_major_locator(MultipleLocator(300 * 12))
ax.xaxis.set_major_formatter(FuncFormatter(time_formatter))
ax.xaxis.set_minor_locator( MultipleLocator(300) )

fig.set_size_inches(20, 10.5)
plt.savefig("/var/http/slowrate.png")







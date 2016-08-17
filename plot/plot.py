# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2016-08-17 02:07:56
#    email     :   fengidri@yeah.net
#    version   :   1.0.1



import os
import sys
import json
import time

j = open('slow_rate.json').read()
data = json.loads(j)['data']

keys = [ int(x) for x in data.keys()]
keys.sort()

values = [data[str(k)][0][1] for k in keys]

def time_formatter(timestamp, pos):
    "show time hour and mins look like: HH:MM"
    timestamp += 8 * 3600

    return time.strftime("%H:%M", time.gmtime(timestamp))

#####################################################
opt_x      = keys
opt_y      = values
opt_title  = "MG"
opt_xlabel = "Time"
opt_ylabel = "SlowRate"
#####################################################

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter

plt.figure(figsize=(20, 10.5))
plt.plot(opt_x, opt_y)
plt.xlabel(opt_xlabel)
plt.ylabel(opt_ylabel)
plt.title(opt_title)
#plt.ylim()
#plt.legend()

ax = plt.gca()
ax.xaxis.set_major_locator(MultipleLocator(300 * 12))
ax.xaxis.set_major_formatter(FuncFormatter(time_formatter))
ax.xaxis.set_minor_locator( MultipleLocator(300) )

plt.savefig("/var/http/slowrate.png")







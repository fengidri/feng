# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2017-04-27 09:59:05
#    email     :   fengidri@yeah.net
#    version   :   1.0.1


if __name__ == "__main__":
    pass

import requests
import sys
import time


request_url = sys.argv[1]
if request_url.startswith('http://'):
    request_host = request_url.split("/")[2]
else:
    request_host = request_url.split("/")[0]


ts_urls = []


def reget():
    wait_status = False
    m3u8 = requests.get(request_url).text.split('\n')

    for url in m3u8:
        if not url:
            continue

        if url[0] == '#':
            continue

        if url[0] == '/':
            url = "http://%s%s" % (request_host, url)

        elif url.startswith('http://'):
            pass
        else:
            u = request_url.split('/')
            u[-1] = url
            url = '/'.join(u)

        if url in ts_urls:
            wait_status = True
            print '.',
            continue
        else:
            ts_urls.append(url)
            if wait_status:
                wait_status = False
                print ''

        s = time.time()
        res = requests.get(url)
        e = time.time()

        print res.status_code, "%.3f" % (e - s), url




def main():
    while True:
        reget()
        time.sleep(5)

main()

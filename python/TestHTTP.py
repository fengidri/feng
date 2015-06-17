# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-06-17 10:57:47
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urlparse
class TestHTTPHandle(BaseHTTPRequestHandler):
    def do_GET(self):
        self.body_len = 0
        self.chunked = False
        self.auto_content_length = True

        self.protocol_version = "HTTP/1.1"

        self.send_response(200)
        self.handle_header_from_query()
        if self.auto_content_length:
            self.send_header('Content-Length', self.body_len)
        self.end_headers()

        if not self.chunked:
            self.wfile.write('A' * self.body_len)
        else:
            sended = 0
            while sended < self.body_len:
                chunk_len = min(1024, self.body_len - sended)
                sended += chunk_len
                self.wfile.write('%X\r\n%s\r\n' % (chunk_len, 'A' * chunk_len))
            self.wfile.write('0\r\n\r\n')

    def handle_header_from_query(self):
        t = self.path.split('?', 1)
        if len(t) == 1:
            return

        querys = [ss.split('=', 1) for ss in t[1].split('&')]
        for k, v in querys:
            if k.startswith('H-'):
                self.send_header(k[2:], v)
                if k == 'H-Content-Length':
                    self.auto_content_length = False

            if k == 'bodylen':
                self.body_len = int(v)

            if k == 'chunked':
                self.send_header('Transfer-Encoding', 'chunked')
                self.chunked = True
                self.auto_content_length = False

def main():
    http_server = HTTPServer(('127.0.0.1', 8989), TestHTTPHandle)
    http_server.serve_forever()

if __name__ == "__main__":
    main()


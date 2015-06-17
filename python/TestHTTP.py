# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-06-17 10:57:47
#    email     :   fengidri@yeah.net
#    version   :   1.0.1

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urlparse
import socket
class HTTPRequestHandler(BaseHTTPRequestHandler):
    index = 0
    def log_request_(self):
        print '[%s] >>>>>>>>>>>>>>>>>>>>>>>>>>' % self.__class__.index
        print self.requestline
        self.response_header = []

        m = 0
        for k, v in self.headers.items():
            m = max(m, len(k))

        for k, v in self.headers.items():
            print "%s:%s %s" % (k, ' '*(m - len(k)), v)
        print ''
        self.__class__.index += 1

    def log_request(self, code=None):
        print self.protocol_version, code, self.responses[code][0]

    def log_response(self):
        m = 0
        for k, v in self.response_header:
            m = max(m, len(k))

        for k, v in self.response_header:
            print "%s:%s %s" % (k, ' '*(m - len(k)), v)
        print ''


    def send_header(self, keyword, value):
        BaseHTTPRequestHandler.send_header(self, keyword, value)
        self.response_header.append((keyword, value))


    def version_string(self):
        """Return the server software version string."""
        return 'TestHttp'

    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(501, "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            self.log_request_()
            method()
            self.log_response()
            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout, e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return


class TestHTTPHandle(HTTPRequestHandler):

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


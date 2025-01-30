import socket
from http.server import SimpleHTTPRequestHandler
import socketserver
from sys import argv
from os import chdir

# Thanks! https://stackoverflow.com/a/18858817/2078761
# Absolutely essential!  This ensures that socket resuse is setup BEFORE
# it is bound.  Will avoid the TIME_WAIT issue
class MyTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

PORT = 8000

chdir(argv[1])

print(f'Serving {argv[1]} at https://localhost:{PORT}')

Handler = SimpleHTTPRequestHandler

Handler.extensions_map={
    '.html': 'text/html',
    '': 'text/html', # Default is 'application/octet-stream'
    }

httpd = MyTCPServer(("", PORT), Handler)

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.shutdown()


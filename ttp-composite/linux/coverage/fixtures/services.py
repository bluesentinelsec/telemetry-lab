#!/usr/bin/env python3
"""Private fixture services. They perform no adversary behavior or test dispatch."""
import http.server
import socket
import sys
from pathlib import Path
PAYLOAD=b'telemetry-lab-fixture\n'
mode=sys.argv[1]
if mode=='http':
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path!='/fixture':self.send_error(404);return
            self.send_response(200);self.send_header('Content-Length',str(len(PAYLOAD)));self.end_headers();self.wfile.write(PAYLOAD)
        def log_message(self,*args):pass
    http.server.HTTPServer(('198.18.0.1',18080),Handler).serve_forever()
else:
    port={'send':4445,'netcat':4444,'shell':4446}[mode]
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind(('198.18.0.1',port));server.listen(8)
        while True:
            conn,_=server.accept()
            with conn:
                conn.settimeout(5)
                if mode=='send':conn.sendall(PAYLOAD);continue
                if mode=='shell':conn.sendall(b"printf 'SHELL_OK'; exit\n")
                data=b''
                while (b'NETCAT_OK' if mode=='netcat' else b'SHELL_OK') not in data:
                    chunk=conn.recv(4096)
                    if not chunk:break
                    data+=chunk
                expected=b'NETCAT_OK' if mode=='netcat' else b'SHELL_OK'
                if expected in data:
                    Path('/tmp/lab/peer-raw').write_bytes(data)
                    Path('/tmp/lab/received').write_bytes(expected)

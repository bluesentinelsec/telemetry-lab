#!/usr/bin/env python3
"""Private fixture services. They perform no adversary behavior or test dispatch."""
import http.server
import socket
import sys
from pathlib import Path
PAYLOAD=b'telemetry-lab-fixture\n'
# Interactive shells echo input: only executed output contains SHELL_OK.
SHELL_COMMAND=b'printf \'SHELL_%s\' OK; read ack; test "$ack" = ACK; exit\n'

def handle_peer(conn, mode, directory):
    conn.settimeout(5)
    if mode=='send':
        conn.sendall(PAYLOAD)
        return True
    if mode=='shell':
        conn.sendall(SHELL_COMMAND)
    expected=b'NETCAT_OK' if mode=='netcat' else b'SHELL_OK'
    data=b''
    while expected not in data:
        chunk=conn.recv(4096)
        if not chunk:return False
        data+=chunk
        if len(data)>65536:raise RuntimeError('Unexpected fixture response size')
    (directory/'peer-raw').write_bytes(data)
    (directory/'received').write_bytes(expected)
    if mode=='shell':
        # Publish verification before the shell may finish, then drain until
        # it exits. Early close can send SIGHUP during successful execution.
        conn.sendall(b'ACK\n')
        while conn.recv(4096):pass
    return True

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/fixture':self.send_error(404);return
        self.send_response(200);self.send_header('Content-Length',str(len(PAYLOAD)));self.end_headers();self.wfile.write(PAYLOAD)
    def log_message(self,*args):pass

def main():
    mode=sys.argv[1]
    if mode=='http':
        http.server.HTTPServer(('198.18.0.1',18080),Handler).serve_forever()
        return
    port={'send':4445,'netcat':4444,'shell':4446}[mode]
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind(('198.18.0.1',port));server.listen(8)
        while True:
            conn,_=server.accept()
            with conn:handle_peer(conn,mode,Path('/tmp/lab'))

if __name__=='__main__':main()

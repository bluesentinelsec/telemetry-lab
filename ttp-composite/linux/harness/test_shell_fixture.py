import importlib.util
from pathlib import Path
import socket
import tempfile
import threading
import unittest

p=Path(__file__).with_name('fixtures')/'services.py'
spec=importlib.util.spec_from_file_location('fixture_services',p)
services=importlib.util.module_from_spec(spec);spec.loader.exec_module(services)

class ShellFixtureTests(unittest.TestCase):
    def test_echoed_input_is_not_execution_and_ack_follows_verified_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client,server=socket.socketpair();outcome=[]
            def run():
                with server:outcome.append(services.handle_peer(server,'shell',root))
            thread=threading.Thread(target=run);thread.start()
            with client:
                client.settimeout(5);command=client.recv(4096)
                self.assertNotIn(b'SHELL_OK',command)
                client.sendall(command)  # An interactive shell echoes the command.
                client.settimeout(.05)
                with self.assertRaises(socket.timeout):client.recv(4096)
                self.assertFalse((root/'received').exists())
                client.sendall(b'SHELL_OK')  # Only actual execution produces this.
                client.settimeout(5);self.assertEqual(client.recv(4096),b'ACK\n')
                self.assertEqual((root/'received').read_bytes(),b'SHELL_OK')
                client.shutdown(socket.SHUT_WR)
            thread.join(5);self.assertFalse(thread.is_alive());self.assertEqual(outcome,[True])

    def test_disconnect_without_execution_has_no_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);client,server=socket.socketpair()
            client.shutdown(socket.SHUT_WR)
            with server:self.assertFalse(services.handle_peer(server,'shell',root))
            client.close();self.assertFalse((root/'received').exists())

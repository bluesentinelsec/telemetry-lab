import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from verify_programs import verify


class ProgramContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        manifest=json.loads(Path(__file__).with_name('manifest.json').read_text())
        self.ids=[c['id'] for c in manifest['cases']]+['negative']
        for name in self.ids:
            (self.root/name).write_bytes(b'\x7fELF'+('CASE_OK '+name+'\0').encode())
        (self.root/'fixture_prepare').write_bytes(b'\x7fELFfixture_prepare')
        self.loader=patch('verify_programs.subprocess.check_output',return_value='ld-linux-x86-64.so.2')
        self.loader.start()

    def tearDown(self):
        self.loader.stop();self.temp.cleanup()

    def test_dispatcher_or_wrapper_is_rejected(self):
        target=self.root/self.ids[0]
        target.write_bytes(target.read_bytes()+('CASE_OK '+self.ids[1]+'\0').encode())
        with self.assertRaisesRegex(ValueError,'unrelated case markers'):verify(self.root,'glibc')
        target.write_text('#!/bin/sh\nexec ../falco_cases example\n')
        with self.assertRaisesRegex(ValueError,'standalone ELF'):verify(self.root,'glibc')

    def test_extra_dispatcher_missing_program_and_wrong_loader_are_rejected(self):
        (self.root/'falco_cases').write_bytes(b'\x7fELF')
        with self.assertRaisesRegex(ValueError,'roster differs'):verify(self.root,'glibc')
        (self.root/'falco_cases').unlink()
        with self.assertRaisesRegex(ValueError,'wrong runtime loader'):verify(self.root,'musl')
        (self.root/self.ids[0]).unlink()
        with self.assertRaisesRegex(ValueError,'roster differs'):verify(self.root,'glibc')

    def test_cpp_requires_correct_library_and_real_symbol_use(self):
        for runtime,needed,symbol in [('libstdcxx','libstdc++.so.6','GLIBCXX_3.4'),
                                      ('libcxx','libc++.so.1','_ZNSt3__1abc')]:
            def output(args, **kwargs):
                if '-l' in args: return 'ld-linux-x86-64.so.2'
                if '-d' in args: return f'NEEDED [{needed}]'
                return ' UND '+symbol
            with patch('verify_programs.subprocess.check_output',side_effect=output):
                verify(self.root,runtime)
            with patch('verify_programs.subprocess.check_output',return_value='ld-linux-x86-64.so.2'):
                with self.assertRaisesRegex(ValueError,r'wrong C\+\+ standard library'):
                    verify(self.root,runtime)
            def unused(args, **kwargs):
                return output(args) if '--dyn-syms' not in args else ''
            with patch('verify_programs.subprocess.check_output',side_effect=unused):
                with self.assertRaisesRegex(ValueError,'does not use'):
                    verify(self.root,runtime)

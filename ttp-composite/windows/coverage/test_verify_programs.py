"""Reject invalid runtime comparisons before running a Windows campaign."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from verify_programs import verify_imports
from bundle_runtime import bundle


class RuntimeTests(unittest.TestCase):
    def test_cpp_requires_selected_library_and_ucrt(self):
        for runtime, library, other in [('libstdcxx','libstdc++-6.dll','libc++.dll'),
                                         ('libcxx','libc++.dll','libstdc++-6.dll')]:
            verify_imports(['KERNEL32.dll','api-ms-win-crt-runtime-l1-1-0.dll',library],runtime,'probe')
            for imports in [[library,'msvcrt.dll'], ['ucrtbase.dll'],
                            ['ucrtbase.dll',library,other], ['ucrtbase.dll',library,'msvcrt.dll']]:
                with self.assertRaises(ValueError):verify_imports(imports,runtime,'probe')

    def test_c_axis_still_rejects_mixed_crts(self):
        verify_imports(['msvcrt.dll'],'msvcrt','probe')
        verify_imports(['ucrtbase.dll'],'ucrt','probe')
        for runtime in ['ucrt','msvcrt']:
            with self.assertRaises(ValueError):
                verify_imports(['ucrtbase.dll','msvcrt.dll'],runtime,'probe')

    def test_bundle_follows_indirect_imports_in_nested_program_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);dist=root/'dist';runtime=root/'bin';runtime.mkdir()
            for name in ['libc++.dll','libunwind.dll']:(runtime/name).write_bytes(name.encode())
            for directory in [dist,dist/'coverage',dist/'coverage/fixtures']:
                directory.mkdir(parents=True,exist_ok=True);(directory/'probe.exe').write_bytes(b'MZ')
            imports={'probe.exe':['KERNEL32.dll','libc++.dll'],
                     'libc++.dll':['libunwind.dll'], 'libunwind.dll':['libc++.dll','ucrtbase.dll']}
            with patch('bundle_runtime.pe_imports',side_effect=lambda p,_:imports[p.name]):
                bundle(dist,runtime)
            for directory in [dist,dist/'coverage',dist/'coverage/fixtures']:
                for name in ['libc++.dll','libunwind.dll']:
                    self.assertEqual((directory/name).read_bytes(),(runtime/name).read_bytes())
                self.assertFalse((directory/'KERNEL32.dll').exists())


if __name__=='__main__':unittest.main()

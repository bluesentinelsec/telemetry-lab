"""Reject invalid runtime comparisons before running a Windows campaign."""
import tempfile
import struct
import unittest
from pathlib import Path
from unittest.mock import patch
from verify_programs import verify_imports, verify_go, verify_rust, pe_imports
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

    def test_go_requires_real_cgo_linkage_and_matching_metadata(self):
        for runtime,flag,symbol in [('go-cgo','1','runtime/cgo.goStart'),('go-static','0','runtime.main')]:
            info=f"build CGO_ENABLED={flag}\nbuild GOOS=windows\nbuild GOARCH=amd64\n"
            verify_go(info,symbol,runtime,'probe')
            with self.assertRaises(ValueError):verify_go(info.replace('windows','linux'),symbol,runtime,'probe')
            wrong='runtime.main' if flag=='1' else 'runtime/cgo.goStart'
            with self.assertRaises(ValueError):verify_go(info,wrong,runtime,'probe')
        verify_imports(['ucrtbase.dll','KERNEL32.dll'],'go-cgo','probe')
        verify_imports(['KERNEL32.dll'],'go-static','probe')
        with self.assertRaises(ValueError):verify_imports(['msvcrt.dll'],'go-cgo','probe')
        with self.assertRaises(ValueError):verify_imports(['ucrtbase.dll'],'go-static','probe')

    def test_rust_linkage_is_verified_in_binary_and_metadata(self):
        dynamic=['kernel32.dll','ucrtbase.dll','VCRUNTIME140.dll']
        verify_imports(dynamic,'rust-msvc-dynamic','probe')
        verify_imports(['kernel32.dll'],'rust-msvc-static','probe')
        for names,runtime in [(dynamic,'rust-msvc-static'),(['kernel32.dll'],'rust-msvc-dynamic'),(['ucrtbase.dll'],'rust-msvc-dynamic'),(['msvcrt.dll'],'rust-msvc-static')]:
            with self.assertRaises(ValueError):verify_imports(names,runtime,'probe')
        for crt,flag in [('dynamic','-'),('static','+')]:
            data=f'RUST_TARGET x86_64-pc-windows-msvc\nRUST_CRT {crt}\n'.encode()
            metadata={'target':'x86_64-pc-windows-msvc','crt':crt,'rustflags':f'-C target-feature={flag}crt-static'}
            verify_rust(data,metadata,'rust-msvc-'+crt,'probe')
            with self.assertRaises(ValueError):verify_rust(data.replace(b'msvc',b'gnu'),metadata,'rust-msvc-'+crt,'probe')
            with self.assertRaises(ValueError):verify_rust(data,{**metadata,'rustflags':''},'rust-msvc-'+crt,'probe')
            with self.assertRaises(ValueError):verify_rust(data,{**metadata,'target':'x86_64-pc-windows-gnu'},'rust-msvc-'+crt,'probe')

    def test_pe_imports_follow_rva_not_debug_section_contents(self):
        data=bytearray(0x600);data[:2]=b'MZ';struct.pack_into('<I',data,0x3c,0x80)
        data[0x80:0x84]=b'PE\0\0';struct.pack_into('<HH',data,0x84,0x8664,2)
        struct.pack_into('<H',data,0x94,240);optional=0x98
        struct.pack_into('<H',data,optional,0x20b)
        struct.pack_into('<I',data,optional+108,16)
        struct.pack_into('<II',data,optional+120,0x2000,40)
        for i,(name,rva,raw) in enumerate([(b'.zdebug',0x1000,0x200),(b'.idata',0x2000,0x400)]):
            section=optional+240+40*i;data[section:section+len(name)]=name
            struct.pack_into('<IIII',data,section+8,0x200,rva,0x200,raw)
        # Unrelated strings/debug data must not be mistaken for imports.
        data[0x200:0x20a]=b'msvcrt.dll'
        struct.pack_into('<IIIII',data,0x400,0x2080,0,0,0x2050,0x2090)
        data[0x450:0x45d]=b'kernel32.dll\0'
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'probe.exe';p.write_bytes(data)
            self.assertEqual(pe_imports(p),['kernel32.dll'])
            for offset,value in [(0x400+12,0x8000),(optional+120,0),(0x420,1)]:
                broken=bytearray(data);struct.pack_into('<I',broken,offset,value);p.write_bytes(broken)
                with self.assertRaises(ValueError):pe_imports(p)

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

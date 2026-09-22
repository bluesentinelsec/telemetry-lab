"""Ensure the C, C++, Go, and Rust suites survive release assembly without inventing ports."""
import json
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path


class ReleaseTests(unittest.TestCase):
    def test_implemented_coverage_is_packaged_with_its_pinned_mapping(self):
        repo=Path(__file__).resolve().parents[3]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);components=root/'components';output=root/'out'
            def fixture(name):
                p=components/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
            for name in ('tmon-linux/tmon','tmon-windows/tmon.exe','tap/linux/tap','tap/windows/tap.exe'):
                fixture(name)
            linux=['linux-c-glibc','linux-c-musl','linux-cpp-libstdcxx','linux-cpp-libcxx',
                   'linux-go-cgo','linux-go-static','linux-rust-gnu','linux-rust-musl']
            windows=['windows-c-ucrt','windows-c-msvcrt','windows-cpp-libstdcxx',
                     'windows-cpp-libcxx','windows-go-cgo','windows-go-static']
            for config in linux+windows:
                fixture(config+'/empty'+('.exe' if config.startswith('windows') else ''))
                fixture('composite-'+config+'/reverse_shell'+('.exe' if config.startswith('windows') else ''))
            for config in linux:
                fixture('composite-'+config+'/falco_helper')
                ids=[c['id'] for c in json.loads((repo/'ttp-composite/linux/coverage/manifest.json').read_text())['cases']]
                for name in ids+['negative','fixture_prepare']:
                    fixture('composite-'+config+'/coverage/'+name)
                    (components/('composite-'+config+'/coverage/'+name)).write_text('standalone '+name)
            for config in windows:
                fixture('composite-'+config+'/coverage/registry_run_key.exe')
                fixture('composite-'+config+'/coverage/build-manifest.json')
                fixture('composite-'+config+'/coverage/fixtures/windows_fixture_helper.exe')
            for config in windows[2:4]:
                fixture('composite-'+config+'/coverage/libfixture.dll')
            subprocess.run(['bash','scripts/assemble-release.sh','test',str(components),str(output)],
                           cwd=repo,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            with tarfile.open(output/'telemetry-lab-test-linux.tar.gz') as archive:
                names=set(archive.getnames());prefix='telemetry-lab-test-linux/ttp-composite/'
                for config in linux:
                    for name in ids+['negative','fixture_prepare']:
                        self.assertIn(prefix+config+'/coverage/'+name,names)
                    self.assertNotIn(prefix+config+'/falco_cases',names)
                    self.assertIn(prefix+config+'/falco_helper',names)
                original=archive.extractfile(prefix+'linux-c-glibc/reverse_shell').read()
                self.assertEqual(original,b'fixture')
                self.assertIn(prefix+'coverage/manifest.json',names)
                self.assertIn(prefix+'coverage/rules/falco_rules.yaml',names)
            with zipfile.ZipFile(output/'telemetry-lab-test-windows.zip') as archive:
                names=set(archive.namelist());prefix='telemetry-lab-test-windows/ttp-composite/'
                for config in windows:
                    self.assertIn(prefix+config+'/coverage/registry_run_key.exe',names)
                    self.assertIn(prefix+config+'/coverage/build-manifest.json',names)
                    self.assertIn(prefix+config+'/coverage/fixtures/windows_fixture_helper.exe',names)
                for config in windows[2:4]:
                    self.assertIn(prefix+config+'/coverage/libfixture.dll',names)
                for support in ['selection.json','rule-inventory.csv','run.ps1','run-local-tcp.ps1','run-local-dns.ps1','analyze.py']:
                    self.assertIn(prefix+'coverage/'+support,names)


if __name__=='__main__': unittest.main()

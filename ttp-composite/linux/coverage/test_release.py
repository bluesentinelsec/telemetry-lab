"""Ensure the new C-only suite survives release assembly without inventing ports."""
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


class ReleaseTests(unittest.TestCase):
    def test_c_coverage_is_packaged_with_its_pinned_mapping(self):
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
            for config in linux[:2]:
                fixture('composite-'+config+'/falco_cases');fixture('composite-'+config+'/falco_helper')
            subprocess.run(['bash','scripts/assemble-release.sh','test',str(components),str(output)],
                           cwd=repo,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            with tarfile.open(output/'telemetry-lab-test-linux.tar.gz') as archive:
                names=set(archive.getnames());prefix='telemetry-lab-test-linux/ttp-composite/'
                for config in linux[:2]:
                    self.assertIn(prefix+config+'/falco_cases',names)
                    self.assertIn(prefix+config+'/falco_helper',names)
                self.assertNotIn(prefix+'linux-go-cgo/falco_cases',names)
                self.assertIn(prefix+'coverage/manifest.json',names)
                self.assertIn(prefix+'coverage/rules/falco_rules.yaml',names)


if __name__=='__main__': unittest.main()

"""Ensure archive-backed reads preserve bytes, hashes, and glob boundaries."""
import hashlib,importlib.util,io,tarfile,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('archive_io',Path(__file__).with_name('archive_io.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ArchiveTests(unittest.TestCase):
 def test_exact_bytes_hash_and_glob(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/'evidence.tar.gz'
   payloads={'inventory.json':b'{"os":"linux"}\n','primitives/raw/a.jsonl':b'{"event":1}\n','composites/batch-00000/health.json':b'{}\n','composites/batch-00016/health.json':b'{}\n','composites/nested/collector-restart-hidden.json':b'{}','composites/collector-restart-000016.json':b'{}'}
   with tarfile.open(p,'w:gz') as tar:
    for name,data in payloads.items():
     item=tarfile.TarInfo('./'+name);item.size=len(data);tar.addfile(item,io.BytesIO(data))
   with module.evidence_archive(p,root) as virtual:
    for name,data in payloads.items():
     f=virtual/name;self.assertTrue(f.exists());self.assertEqual(f.read_bytes(),data)
     with f.open('rb') as source:self.assertEqual(hashlib.file_digest(source,'sha256').hexdigest(),hashlib.sha256(data).hexdigest())
    self.assertEqual(len(list((virtual/'composites').glob('batch-*/health.json'))),2)
    self.assertEqual([f.name for f in (virtual/'composites').glob('collector-restart-*.json')],['collector-restart-000016.json'])
    self.assertEqual((virtual/'composites/batch-00016/health.json').parent.name,'batch-00016')
    self.assertFalse((virtual/'absent.json').exists())
    with self.assertRaises(ValueError):virtual/'../outside'

if __name__=='__main__':unittest.main()

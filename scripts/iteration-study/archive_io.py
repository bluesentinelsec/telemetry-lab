"""Read evidence from one decompressed tar file without materializing tiny files."""
import contextlib,fnmatch,gzip,shutil,tarfile,tempfile
from pathlib import PurePosixPath

class ArchivePath:
 def __init__(self,archive,index,path='.'):
  self.archive,self.index,self.path=archive,index,PurePosixPath(path)
 def __truediv__(self,other):
  part=PurePosixPath(other)
  if part.is_absolute() or '..' in part.parts:raise ValueError('Evidence paths must remain relative')
  return ArchivePath(self.archive,self.index,self.path/part)
 @property
 def name(self):return self.path.name
 @property
 def suffix(self):return self.path.suffix
 @property
 def parent(self):return ArchivePath(self.archive,self.index,self.path.parent)
 def exists(self):return self.path.as_posix() in self.index
 def is_dir(self):return self.exists() and self.index[self.path.as_posix()].isdir()
 def glob(self,pattern):
  prefix='' if self.path.as_posix()=='.' else self.path.as_posix()+'/'
  depth=len(PurePosixPath(pattern).parts)
  for name in self.index:
   if not name.startswith(prefix):continue
   relative=name[len(prefix):]
   if len(PurePosixPath(relative).parts)==depth and fnmatch.fnmatchcase(relative,pattern):
    yield ArchivePath(self.archive,self.index,name)
 def open(self,mode='rb'):
  if mode!='rb':raise ValueError('Archive evidence is read-only binary data')
  member=self.index[self.path.as_posix()]
  if not member.isfile():raise ValueError('Expected a regular evidence file')
  return self.archive.extractfile(member)
 def read_bytes(self):
  with self.open() as f:return f.read()
 def read_text(self,encoding='utf-8-sig'):return self.read_bytes().decode(encoding)
 def __str__(self):return 'archive:'+self.path.as_posix()

@contextlib.contextmanager
def evidence_archive(path,tempdir):
 # A single temporary uncompressed tar supports cheap random reads. Seeking
 # backward through the compressed stream for every record would be quadratic.
 with tempfile.TemporaryFile(dir=tempdir) as spool:
  with gzip.open(path,'rb') as source:shutil.copyfileobj(source,spool,1024*1024)
  spool.seek(0)
  with tarfile.open(fileobj=spool,mode='r:') as archive:
   index={}
   for member in archive.getmembers():
    name=PurePosixPath(member.name)
    if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe evidence member')
    key=name.as_posix()
    if key in index:raise ValueError('Duplicate evidence member: '+key)
    index[key]=member
   yield ArchivePath(archive,index)

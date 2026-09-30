#!/usr/bin/env python3
"""Automated per-container setup, completed outside the measurement window."""
import json,os,socket,subprocess,sys,time
from pathlib import Path
case,config=sys.argv[1:3]
p=Path('/tmp/lab');p.mkdir(exist_ok=True)
def run(*args):return subprocess.run(args,check=True,capture_output=True,text=True).stdout
def service(args):
    with (p/'service-startup.log').open('ab') as log:
        child=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    return child

def wait_port(ip,port,child):
    for _ in range(100):
        if child.poll() is not None:raise RuntimeError((p/'service-startup.log').read_text())
        # Inspect listening sockets instead of consuming the fixture's first connection.
        if f':{port:04X} ' in Path('/proc/net/tcp').read_text():return
        time.sleep(.05)
    raise RuntimeError(f'Fixture port {port} never opened')

Path('/root/.bashrc').write_text('telemetry-lab-fixture\n')
(p/'executable-mode').write_text('inert\n');(p/'executable-mode').chmod(0o600)
(p/'shred-target').write_bytes(b'X'*64)
for name in ['mount-source','mount-target','transfer']:(p/name).mkdir(exist_ok=True)
(p/'mount-source/payload').write_text('telemetry-lab-fixture\n')
(p/'transfer/payload').write_text('telemetry-lab-fixture\n')
for mode,cases,port in [('http',{'proxy_environment','ingress_copy','web_child'},18080),('send',{'network_tool','shell_network','npm_network_tool'},4445),('netcat',{'netcat_exec'},4444),('shell',{'web_reverse_shell'},4446)]:
    if case in cases:
        child=service(['/usr/bin/python3','/opt/lab-fixtures/services.py',mode]);wait_port('198.18.0.1',port,child)
if case=='privileged_debugfs':
    with (p/'filesystem.img').open('wb') as f:f.truncate(8*1024*1024)
    run('/usr/sbin/mke2fs','-q','-F',str(p/'filesystem.img'))
    run('/usr/sbin/debugfs','-w','-R',f'write {p}/transfer/payload /marker',str(p/'filesystem.img'))
if case=='remote_copy':
    (p/'rsync.conf').write_text('pid file = /tmp/lab/rsync.pid\nport = 1873\nuse chroot = no\nuid = root\ngid = root\n[fixture]\npath = /tmp/lab/transfer\nread only = yes\n')
    child=service(['/usr/bin/rsync','--daemon','--no-detach','--config=/tmp/lab/rsync.conf']);wait_port('198.18.0.1',1873,child)
if case=='ssh_nonstandard':
    p.chmod(0o755)
    Path('/run/sshd').mkdir(exist_ok=True)
    run('/usr/bin/ssh-keygen','-q','-t','ed25519','-N','','-f',str(p/'sshkey'))
    run('/usr/bin/ssh-keygen','-q','-t','ed25519','-N','','-f',str(p/'hostkey'))
    (p/'authorized_keys').write_text((p/'sshkey.pub').read_text())
    (p/'known_hosts').write_text('[198.18.0.1]:4444 '+(p/'hostkey.pub').read_text())
    # The base sensitive-file fixture replaces shadow. Restore only an unusable
    # password entry for this key-only test account; password auth stays disabled.
    Path('/etc/shadow').write_text('labfixture:x:20000:0:99999:7:::\n')
    (p/'sshd.conf').write_text('Port 4444\nListenAddress 198.18.0.1\nHostKey /tmp/lab/hostkey\nPidFile /tmp/lab/sshd.pid\nAuthorizedKeysFile /tmp/lab/authorized_keys\nStrictModes no\nUsePAM no\nPasswordAuthentication no\nKbdInteractiveAuthentication no\nPubkeyAuthentication yes\nAllowUsers labfixture\n')
    child=service(['/usr/sbin/sshd','-D','-e','-f',str(p/'sshd.conf')]);wait_port('198.18.0.1',4444,child)
if case in {'protected_shell','web_shell','web_child','web_reverse_shell'}:
    # A real prefork Apache worker directly executes the native CGI executable.
    # No shell wrapper and no executable renaming is involved.
    config_text=f'''ServerRoot /etc/apache2
ServerName localhost
Listen 127.0.0.1:18082
PidFile /tmp/lab/apache.pid
LoadModule mpm_prefork_module /usr/lib/apache2/modules/mod_mpm_prefork.so
LoadModule authz_core_module /usr/lib/apache2/modules/mod_authz_core.so
LoadModule env_module /usr/lib/apache2/modules/mod_env.so
LoadModule alias_module /usr/lib/apache2/modules/mod_alias.so
LoadModule cgi_module /usr/lib/apache2/modules/mod_cgi.so
User www-data
Group www-data
ErrorLog /tmp/lab/apache-error
LogLevel error
StartServers 1
MinSpareServers 1
MaxSpareServers 1
MaxRequestWorkers 1
SetEnv TELEMETRY_LAB_FIXTURE 1
ScriptAlias /measured /opt/coverage/{config}/coverage/{case}
<Directory /opt/coverage/{config}/coverage>
Options +ExecCGI
Require all granted
</Directory>
'''
    (p/'apache.conf').write_text(config_text)
    p.chmod(0o777)
    child=service(['/usr/sbin/apache2','-f',str(p/'apache.conf'),'-DFOREGROUND']);wait_port('127.0.0.1',18082,child)
if case=='npm_network_tool':
    d=p/'npm';d.mkdir(exist_ok=True)
    # Use the real npm install lifecycle; no registry or network dependencies.
    exe=f'/opt/coverage/{config}/coverage/{case}'
    control=' --control' if len(sys.argv)>3 and sys.argv[3]=='control' else ''
    (d/'package.json').write_text(json.dumps({'name':'telemetry-lab-fixture','version':'1.0.0','private':True,'scripts':{'install':'exec python3 /opt/lab-fixtures/gated_exec.py '+exe+control}}))
    os.mkfifo(p/'native-trigger')
    child=service(['/usr/bin/python3','/opt/lab-fixtures/npm_session.py'])
    for _ in range(200):
        if (p/'native-ready').exists():break
        if child.poll() is not None:raise RuntimeError((p/'npm.stderr').read_text())
        time.sleep(.05)
    else:raise RuntimeError('npm lifecycle did not reach native gate')
print('FIXTURES_READY')

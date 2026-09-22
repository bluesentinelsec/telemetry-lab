//! Shared helpers, not a runtime dispatcher. Each binary has one behavior.
use std::fs::{self, File, OpenOptions};
use std::io::{Read, Write};
use std::net::{Shutdown, TcpListener, TcpStream, UdpSocket};
use std::os::fd::{AsRawFd, FromRawFd, OwnedFd};
use std::os::unix::fs::{DirBuilderExt, OpenOptionsExt, PermissionsExt};
use std::os::unix::process::CommandExt;
use std::process::{Command, Stdio};
use std::time::Duration;

pub const PAYLOAD: &[u8] = b"telemetry-lab-fixture\n";
#[cfg(target_env = "gnu")]
const TARGET: &str = "RUNTIME_TARGET x86_64-unknown-linux-gnu\0";
#[cfg(target_env = "musl")]
const TARGET: &str = "RUNTIME_TARGET x86_64-unknown-linux-musl\0";

pub fn begin(id: &str) -> bool {
    std::hint::black_box(TARGET);
    assert!(
        std::path::Path::new("/.dockerenv").exists(),
        "disposable container required"
    );
    assert_eq!(std::env::var("TELEMETRY_LAB_FIXTURE").as_deref(), Ok("1"));
    let args: Vec<_> = std::env::args().collect();
    assert!(args.len() == 1 || (args.len() == 2 && args[1] == "--control"));
    // No watchdog thread: the ptrace fixtures fork a single-threaded process.
    unsafe {
        libc::alarm(10);
    }
    if args.len() == 2 {
        println!("CONTROL_OK {id}");
        false
    } else {
        true
    }
}
pub fn write_file(path: &str) {
    let mut f = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .mode(0o600)
        .open(path)
        .unwrap();
    f.write_all(PAYLOAD).unwrap();
    drop(f);
    assert_eq!(fs::metadata(path).unwrap().len(), PAYLOAD.len() as u64);
}
pub fn read_file(path: &str) {
    assert_eq!(fs::read(path).unwrap(), PAYLOAD);
}
pub fn truncate_file(path: &str) {
    drop(
        OpenOptions::new()
            .write(true)
            .truncate(true)
            .open(path)
            .unwrap(),
    );
    assert_eq!(fs::metadata(path).unwrap().len(), 0);
}
pub fn directory(path: &str) {
    match fs::DirBuilder::new().mode(0o700).create(path) {
        Ok(()) => (),
        Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {
            assert!(fs::metadata(path).unwrap().is_dir())
        }
        Err(e) => panic!("{e}"),
    }
}
pub fn prepare() {
    for p in [
        "/tmp/lab",
        "/root/.ssh",
        "/etc/cron.d",
        "/etc/apt",
        "/etc/apt/sources.list.d",
        "/boot",
    ] {
        directory(p);
    }
    for p in [
        "/etc/shadow",
        "/var/log/lab.log",
        "/root/.bash_history",
        "/root/.ssh/lab_key",
        "/usr/bin/lab_old",
    ] {
        write_file(p);
    }
}
pub fn metadata_exchange() {
    let ln = TcpListener::bind("169.254.169.254:80").unwrap();
    let mut conn =
        TcpStream::connect_timeout(&ln.local_addr().unwrap(), Duration::from_secs(3)).unwrap();
    let (mut peer, _) = ln.accept().unwrap();
    for s in [&conn, &peer] {
        s.set_read_timeout(Some(Duration::from_secs(3))).unwrap();
        s.set_write_timeout(Some(Duration::from_secs(3))).unwrap();
    }
    conn.write_all(PAYLOAD).unwrap();
    let mut buf = vec![0; PAYLOAD.len()];
    peer.read_exact(&mut buf).unwrap();
    assert_eq!(buf, PAYLOAD);
    peer.write_all(&buf).unwrap();
    conn.read_exact(&mut buf).unwrap();
    assert_eq!(buf, PAYLOAD);
}
pub fn udp_exchange() {
    let peer = UdpSocket::bind("198.18.0.1:44445").unwrap();
    peer.set_read_timeout(Some(Duration::from_secs(3))).unwrap();
    let conn = UdpSocket::bind("0.0.0.0:0").unwrap();
    conn.connect(peer.local_addr().unwrap()).unwrap();
    assert_eq!(conn.send(PAYLOAD).unwrap(), PAYLOAD.len());
    let mut buf = [0; 64];
    let (n, _) = peer.recv_from(&mut buf).unwrap();
    assert_eq!(&buf[..n], PAYLOAD);
}
pub fn reverse_shell() {
    let listener = TcpListener::bind("127.0.0.1:4444").unwrap();
    let handle = std::thread::spawn(move || {
        let (mut peer, _) = listener.accept().unwrap();
        peer.set_read_timeout(Some(Duration::from_secs(5))).unwrap();
        peer.set_write_timeout(Some(Duration::from_secs(5)))
            .unwrap();
        peer.write_all(b"printf 'SHELL_OK\\n'; exit\n").unwrap();
        peer.shutdown(Shutdown::Write).unwrap();
        let mut reply = Vec::new();
        peer.read_to_end(&mut reply).unwrap();
        assert_eq!(reply, b"SHELL_OK\n");
    });
    let sock =
        TcpStream::connect_timeout(&"127.0.0.1:4444".parse().unwrap(), Duration::from_secs(3))
            .unwrap();
    // The existing Rust pilot uses std's socket-to-stdio conversions directly.
    let status = Command::new("/bin/sh")
        .arg0("sh")
        .stdin(Stdio::from(OwnedFd::from(sock.try_clone().unwrap())))
        .stdout(Stdio::from(OwnedFd::from(sock.try_clone().unwrap())))
        .stderr(Stdio::from(OwnedFd::from(sock)))
        .status()
        .unwrap();
    assert!(status.success());
    handle.join().unwrap();
}
pub fn packet_socket() {
    // std has no AF_PACKET interface. htons(ETH_P_ALL) on the frozen target.
    let fd = unsafe {
        libc::socket(
            libc::AF_PACKET,
            libc::SOCK_RAW,
            (libc::ETH_P_ALL as u16).to_be() as i32,
        )
    };
    assert!(fd >= 0, "{}", std::io::Error::last_os_error());
    assert_eq!(unsafe { libc::close(fd) }, 0);
}
pub fn execute_helper(path: &str, memory: bool) {
    let mut dst = if memory {
        let fd = unsafe { libc::memfd_create(c"lab-helper".as_ptr(), 0) };
        assert!(fd >= 0, "{}", std::io::Error::last_os_error());
        unsafe { File::from_raw_fd(fd) }
    } else {
        OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .mode(0o700)
            .open(path)
            .unwrap()
    };
    std::io::copy(&mut File::open("/opt/coverage/helper").unwrap(), &mut dst).unwrap();
    dst.set_permissions(fs::Permissions::from_mode(0o700))
        .unwrap();
    let out = if memory {
        // std has no fexecve interface; retain the memfd across exec and use procfs.
        let result = Command::new(format!("/proc/self/fd/{}", dst.as_raw_fd()))
            .arg0("lab-helper")
            .output()
            .unwrap();
        drop(dst);
        result
    } else {
        drop(dst); // avoid ETXTBSY when executing a writable file
        let result = Command::new(path).output().unwrap();
        fs::remove_file(path).unwrap();
        result
    };
    assert!(out.status.success());
    assert_eq!(out.stdout, b"HELPER_OK\n");
}
fn wait_child(pid: libc::pid_t) -> i32 {
    let mut status = 0;
    loop {
        let got = unsafe { libc::waitpid(pid, &mut status, 0) };
        if got == -1 && std::io::Error::last_os_error().raw_os_error() == Some(libc::EINTR) {
            continue;
        }
        assert_eq!(got, pid);
        return status;
    }
}
pub fn ptrace_attach() {
    // No other threads are started in this binary. The child only calls pause.
    let pid = unsafe { libc::fork() };
    assert!(pid >= 0);
    if pid == 0 {
        loop {
            unsafe {
                libc::pause();
            }
        }
    }
    let null = std::ptr::null_mut::<libc::c_void>();
    assert_eq!(
        unsafe { libc::ptrace(libc::PTRACE_ATTACH, pid, null, null) },
        0
    );
    let status = wait_child(pid);
    assert!(libc::WIFSTOPPED(status) && libc::WSTOPSIG(status) == libc::SIGSTOP);
    assert_eq!(
        unsafe { libc::ptrace(libc::PTRACE_DETACH, pid, null, null) },
        0
    );
    assert_eq!(unsafe { libc::kill(pid, libc::SIGTERM) }, 0);
    let status = wait_child(pid);
    assert!(libc::WIFSIGNALED(status) && libc::WTERMSIG(status) == libc::SIGTERM);
}
pub fn ptrace_traceme() {
    let pid = unsafe { libc::fork() };
    assert!(pid >= 0);
    if pid == 0 {
        let null = std::ptr::null_mut::<libc::c_void>();
        // Only native calls after fork; the parent checks the request via exit status.
        unsafe {
            let rc = libc::ptrace(libc::PTRACE_TRACEME, 0, null, null);
            libc::_exit(if rc == 0 { 0 } else { 1 });
        }
    }
    let status = wait_child(pid);
    assert!(libc::WIFEXITED(status) && libc::WEXITSTATUS(status) == 0);
}

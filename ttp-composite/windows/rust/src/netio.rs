use std::{
    io::{Read, Write},
    net::{Ipv4Addr, SocketAddr, TcpStream, ToSocketAddrs},
    time::Duration,
};
pub fn connect(port: u16) -> TcpStream {
    let s = TcpStream::connect_timeout(
        &SocketAddr::from((Ipv4Addr::LOCALHOST, port)),
        Duration::from_secs(5),
    )
    .unwrap();
    s.set_read_timeout(Some(Duration::from_secs(5))).unwrap();
    s.set_write_timeout(Some(Duration::from_secs(5))).unwrap();
    s
}
pub fn exchange(port: u16) {
    let mut s = connect(port);
    let marker = b"telemetry-lab\n";
    s.write_all(marker).unwrap();
    let mut reply = [0u8; 14];
    s.read_exact(&mut reply).unwrap();
    assert_eq!(&reply, marker, "echo bytes differ");
}
pub fn resolve(name: &str) {
    // Ordinary Rust resolver; IPv4 result is required by the shared fixture.
    // Unlike C's AF_INET hint, std may request both address families. Retain
    // any resulting DNS telemetry as an implementation difference.
    let answers: Vec<_> = (name, 0).to_socket_addrs().unwrap().collect();
    assert!(!answers.is_empty(), "no resolver answers");
    for a in answers {
        assert_eq!(
            a.ip(),
            Ipv4Addr::new(127, 0, 0, 42),
            "unexpected DNS answer"
        );
    }
}

use std::net::{TcpListener,TcpStream};
use std::io::{Read,Write};
use std::time::Duration;
fn main(){if !coverage_suite::begin("miner_port_exchange"){return;}
let ln=TcpListener::bind("198.18.0.1:3333").unwrap();
let mut cli=TcpStream::connect_timeout(&ln.local_addr().unwrap(),Duration::from_secs(3)).unwrap();
let (mut srv,_)=ln.accept().unwrap();
for s in [&cli,&srv] {s.set_read_timeout(Some(Duration::from_secs(3))).unwrap();s.set_write_timeout(Some(Duration::from_secs(3))).unwrap();}
cli.write_all(coverage_suite::PAYLOAD).unwrap();let mut b=vec![0;coverage_suite::PAYLOAD.len()];srv.read_exact(&mut b).unwrap();assert_eq!(b,coverage_suite::PAYLOAD);
srv.write_all(&b).unwrap();cli.read_exact(&mut b).unwrap();assert_eq!(b,coverage_suite::PAYLOAD);
println!("CASE_OK miner_port_exchange");}

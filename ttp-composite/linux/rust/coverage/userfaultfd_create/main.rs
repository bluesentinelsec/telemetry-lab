use coverage_suite as fixture;
fn main() {if !fixture::begin("userfaultfd_create") {return;}
unsafe {assert_eq!(libc::setgid(65534),0);assert_eq!(libc::setuid(65534),0);assert_eq!(libc::getuid(),65534);let fd=libc::syscall(libc::SYS_userfaultfd,libc::O_CLOEXEC|libc::O_NONBLOCK|1) as i32;assert!(fd>=0,"{}",std::io::Error::last_os_error());assert_eq!(libc::close(fd),0);}
println!("CASE_OK userfaultfd_create");
}

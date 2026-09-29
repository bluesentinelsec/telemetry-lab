use coverage_suite as fixture;
use std::os::unix::fs::MetadataExt;
use std::os::fd::AsRawFd;
fn main() {if !fixture::begin("namespace_setns") {return;}
let before=std::fs::metadata("/proc/thread-self/ns/net").unwrap().ino();
let f=std::fs::File::open("/tmp/lab/netns").unwrap(); let target=f.metadata().unwrap().ino(); assert_ne!(before,target); assert_eq!(unsafe {libc::setns(f.as_raw_fd(),libc::CLONE_NEWNET)},0);
 assert_eq!(std::fs::metadata("/proc/thread-self/ns/net").unwrap().ino(),target);
println!("CASE_OK namespace_setns");
}

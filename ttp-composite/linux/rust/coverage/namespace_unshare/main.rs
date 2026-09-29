use coverage_suite as fixture;
use std::os::unix::fs::MetadataExt;
fn main() {if !fixture::begin("namespace_unshare") {return;}
let before=std::fs::metadata("/proc/thread-self/ns/user").unwrap().ino();
assert_eq!(unsafe {libc::unshare(libc::CLONE_NEWUSER)},0); assert_ne!(before,std::fs::metadata("/proc/thread-self/ns/user").unwrap().ino());
println!("CASE_OK namespace_unshare");
}

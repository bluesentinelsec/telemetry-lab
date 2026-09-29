use coverage_suite as fixture;
use std::os::unix::fs::MetadataExt;
fn main() {if !fixture::begin("namespace_unshare_denied") {return;}
let before=std::fs::metadata("/proc/thread-self/ns/net").unwrap().ino();
assert_eq!(unsafe {libc::unshare(libc::CLONE_NEWNET)},-1); assert_eq!(std::io::Error::last_os_error().raw_os_error(),Some(libc::EPERM)); assert_eq!(before,std::fs::metadata("/proc/thread-self/ns/net").unwrap().ino());
println!("CASE_OK namespace_unshare_denied");
}

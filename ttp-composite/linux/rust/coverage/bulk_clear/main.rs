fn main() {
if !coverage_suite::begin("bulk_clear") {return;}
let mut cmd = std::process::Command::new("/usr/bin/shred");
cmd.args(["-n", "0", "-z", "-s", "64", "/tmp/lab/shred-target"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "".as_bytes());
assert_eq!(std::fs::read("/tmp/lab/shred-target").unwrap(), "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".as_bytes());
println!("CASE_OK bulk_clear");
}

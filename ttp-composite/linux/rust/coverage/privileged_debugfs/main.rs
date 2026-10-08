fn main() {
if !coverage_suite::begin("privileged_debugfs") {return;}
let mut cmd = std::process::Command::new("/usr/sbin/debugfs");
cmd.args(["-R", "cat /marker", "/tmp/lab/filesystem.img"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK privileged_debugfs");
}

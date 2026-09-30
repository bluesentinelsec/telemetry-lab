fn main() {
if !coverage_suite::begin("remote_copy") {return;}
let mut cmd = std::process::Command::new("/usr/bin/rsync");
cmd.args(["--port=1873", "rsync://198.18.0.1/fixture/payload", "/tmp/lab/transferred"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "".as_bytes());
assert_eq!(std::fs::read("/tmp/lab/transferred").unwrap(), "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK remote_copy");
}

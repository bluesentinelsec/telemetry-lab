fn main() {
if !coverage_suite::begin("ingress_copy") {return;}
let mut cmd = std::process::Command::new("/usr/bin/curl");
cmd.args(["-fsS", "--noproxy", "*", "http://198.18.0.1:18080/fixture", "-o", "/tmp/lab/downloaded"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "".as_bytes());
assert_eq!(std::fs::read("/tmp/lab/downloaded").unwrap(), "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK ingress_copy");
}

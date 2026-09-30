fn main() {
if !coverage_suite::begin("network_tool") {return;}
let mut cmd = std::process::Command::new("/usr/bin/ncat");
cmd.args(["--recv-only", "198.18.0.1", "4445"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK network_tool");
}

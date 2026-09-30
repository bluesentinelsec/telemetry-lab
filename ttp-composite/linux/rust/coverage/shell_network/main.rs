fn main() {
if !coverage_suite::begin("shell_network") {return;}
let mut cmd = std::process::Command::new("/bin/bash");
cmd.args(["-c", "exec 3<>/dev/tcp/198.18.0.1/4445; cat <&3"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK shell_network");
}

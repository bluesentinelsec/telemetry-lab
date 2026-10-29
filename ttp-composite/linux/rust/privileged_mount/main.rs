// Target rule: Mount Launched in Privileged Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
if !coverage_suite::begin("privileged_mount") {return;}
let mut cmd = std::process::Command::new("/usr/bin/mount");
cmd.args(["--bind", "/tmp/lab/mount-source", "/tmp/lab/mount-target"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "".as_bytes());
assert_eq!(std::fs::read("/tmp/lab/mount-target/payload").unwrap(), "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK privileged_mount");
}

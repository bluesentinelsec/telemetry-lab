// Target rule: Web Server Spawned Suspicious Child Process
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
if !coverage_suite::begin("web_child") {return;}
let mut cmd = std::process::Command::new("/usr/bin/curl");
cmd.args(["-fsS", "--noproxy", "*", "http://198.18.0.1:18080/fixture"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK web_child");
}

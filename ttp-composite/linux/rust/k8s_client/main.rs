// Target rule: Kubernetes Client Tool Launched in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
if !coverage_suite::begin("k8s_client") {return;}
let mut cmd = std::process::Command::new("/usr/bin/docker");
cmd.args(["--version"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert!(out.stdout.starts_with("Docker version ".as_bytes()));
println!("CASE_OK k8s_client");
}

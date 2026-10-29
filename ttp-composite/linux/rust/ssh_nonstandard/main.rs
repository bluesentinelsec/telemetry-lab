// Target rule: Disallowed SSH Connection Non Standard Port
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
if !coverage_suite::begin("ssh_nonstandard") {return;}
let mut cmd = std::process::Command::new("/usr/bin/ssh");
cmd.args(["-F", "/dev/null", "-i", "/tmp/lab/sshkey", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=/tmp/lab/known_hosts", "-p", "4444", "labfixture@198.18.0.1", "/usr/bin/printf SSH_OK"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "SSH_OK".as_bytes());
println!("CASE_OK ssh_nonstandard");
}

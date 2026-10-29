// Target rule: Web Server Spawned Shell
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
if !coverage_suite::begin("web_shell") {return;}
let mut cmd = std::process::Command::new("/bin/sh");
cmd.args(["-c", "printf 'SHELL_OK\\n'"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "SHELL_OK\n".as_bytes());
println!("CASE_OK web_shell");
}

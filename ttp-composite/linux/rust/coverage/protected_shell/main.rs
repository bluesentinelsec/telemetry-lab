fn main() {
if !coverage_suite::begin("protected_shell") {return;}
let mut cmd = std::process::Command::new("/bin/sh");
cmd.args(["-c", "printf 'SHELL_OK\\n'"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "SHELL_OK\n".as_bytes());
println!("CASE_OK protected_shell");
}

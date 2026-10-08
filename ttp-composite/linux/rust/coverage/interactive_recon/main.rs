fn main() {
if !coverage_suite::begin("interactive_recon") {return;}
let mut cmd = std::process::Command::new("/usr/bin/script");
cmd.args(["-q", "-e", "-c", "exec /usr/bin/id -u", "/dev/null"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "0\r\n".as_bytes());
println!("CASE_OK interactive_recon");
}

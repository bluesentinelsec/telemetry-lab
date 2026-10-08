fn main() {
if !coverage_suite::begin("netcat_exec") {return;}
let mut cmd = std::process::Command::new("/usr/bin/ncat");
cmd.args(["--exec", "/usr/bin/printf NETCAT_OK", "198.18.0.1", "4444"]);
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "".as_bytes());
assert_eq!(std::fs::read("/tmp/lab/received").unwrap(), "NETCAT_OK".as_bytes());
println!("CASE_OK netcat_exec");
}

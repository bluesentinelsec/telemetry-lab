fn main() {
if !coverage_suite::begin("proxy_environment") {return;}
let mut cmd = std::process::Command::new("/usr/bin/curl");
cmd.args(["-fsS", "--noproxy", "*", "http://198.18.0.1:18080/fixture"]);
cmd.env("HTTP_PROXY", "http://198.18.0.1:18081");
let out=cmd.output().unwrap(); assert!(out.status.success(), "{:?}", out);
assert_eq!(out.stdout, "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK proxy_environment");
}

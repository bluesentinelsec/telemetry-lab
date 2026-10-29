// Target rule: Potential Local Privilege Escalation via Environment Variables Misuse
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
use coverage_suite as fixture;
fn main() {if !fixture::begin("glibc_tunable_child") {return;}
let out = std::process::Command::new("/opt/coverage/helper").args([] as [&str; 0]).env("GLIBC_TUNABLES","glibc.malloc.trim_threshold=131072").output().unwrap();
 assert!(out.status.success()); assert_eq!(out.stdout, "HELPER_OK\n".as_bytes());
println!("CASE_OK glibc_tunable_child");
}

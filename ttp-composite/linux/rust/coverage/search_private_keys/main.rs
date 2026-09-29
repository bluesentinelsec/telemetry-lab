use coverage_suite as fixture;
fn main() {if !fixture::begin("search_private_keys") {return;}
let out = std::process::Command::new("/usr/bin/grep").args(["BEGIN PRIVATE", "/tmp/lab/key-search"]).output().unwrap();
 assert!(out.status.success()); assert_eq!(out.stdout, "BEGIN PRIVATE KEY telemetry-lab\n".as_bytes());
println!("CASE_OK search_private_keys");
}

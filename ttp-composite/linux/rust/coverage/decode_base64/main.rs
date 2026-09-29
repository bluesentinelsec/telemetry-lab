use coverage_suite as fixture;
fn main() {if !fixture::begin("decode_base64") {return;}
let out = std::process::Command::new("/usr/bin/base64").args(["--decode", "/tmp/lab/encoded"]).output().unwrap();
 assert!(out.status.success()); assert_eq!(out.stdout, "telemetry-lab-fixture\n".as_bytes());
println!("CASE_OK decode_base64");
}

use coverage_suite as fixture;
fn main() {if !fixture::begin("search_aws_credentials") {return;}
let out = std::process::Command::new("/usr/bin/grep").args(["aws_access_key_id", "/tmp/lab/aws-search"]).output().unwrap();
 assert!(out.status.success()); assert_eq!(out.stdout, "aws_access_key_id=telemetry-lab\n".as_bytes());
println!("CASE_OK search_aws_credentials");
}

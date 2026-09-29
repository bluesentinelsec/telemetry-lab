use coverage_suite as fixture;
fn main() {if !fixture::begin("package_manager_query") {return;}
let out = std::process::Command::new("/usr/bin/dpkg").args(["--print-architecture"]).output().unwrap();
 assert!(out.status.success()); assert_eq!(out.stdout, "amd64\n".as_bytes());
println!("CASE_OK package_manager_query");
}

fn main(){if !coverage_suite::begin("identity_change"){return;}
unsafe { assert_eq!(libc::getuid(),0); assert_eq!(libc::setuid(2000),0); assert_eq!(libc::getuid(),2000); assert_eq!(libc::geteuid(),2000); }
println!("CASE_OK identity_change");}

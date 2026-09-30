fn main(){if !coverage_suite::begin("hidden_file"){return;}
coverage_suite::write_file("/tmp/lab/.hidden-fixture"); coverage_suite::read_file("/tmp/lab/.hidden-fixture");
println!("CASE_OK hidden_file");}

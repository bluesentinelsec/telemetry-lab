use coverage_suite as fixture;
fn main() {if !fixture::begin("release_agent_write") {return;}
fixture::write_file("/tmp/lab/release_agent");
println!("CASE_OK release_agent_write");
}

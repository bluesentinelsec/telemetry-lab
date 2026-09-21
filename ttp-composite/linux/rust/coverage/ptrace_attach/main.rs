fn main() {
    if !coverage_suite::begin("ptrace_attach") {
        return;
    }
    coverage_suite::ptrace_attach();
    println!("CASE_OK ptrace_attach");
}

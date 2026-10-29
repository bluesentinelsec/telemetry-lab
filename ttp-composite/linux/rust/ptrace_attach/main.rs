// Target rule: PTRACE attached to process
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("ptrace_attach") {
        return;
    }
    coverage_suite::ptrace_attach();
    println!("CASE_OK ptrace_attach");
}

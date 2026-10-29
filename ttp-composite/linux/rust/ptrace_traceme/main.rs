// Target rule: PTRACE anti-debug attempt
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("ptrace_traceme") {
        return;
    }
    coverage_suite::ptrace_traceme();
    println!("CASE_OK ptrace_traceme");
}

// Target rule: Redirect STDOUT/STDIN to Network Connection in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("reverse_shell") {
        return;
    }
    coverage_suite::reverse_shell();
    println!("CASE_OK reverse_shell");
}

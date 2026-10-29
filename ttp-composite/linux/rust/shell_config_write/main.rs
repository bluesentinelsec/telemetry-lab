// Target rule: Modify Shell Configuration File
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("shell_config_write") {
        return;
    }
    coverage_suite::write_file("/root/.bashrc");
    println!("CASE_OK shell_config_write");
}

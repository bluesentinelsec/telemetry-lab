fn main() {
    if !coverage_suite::begin("reverse_shell") {
        return;
    }
    coverage_suite::reverse_shell();
    println!("CASE_OK reverse_shell");
}

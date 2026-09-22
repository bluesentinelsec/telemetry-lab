fn main() {
    if !coverage_suite::begin("shell_config_write") {
        return;
    }
    coverage_suite::write_file("/root/.bashrc");
    println!("CASE_OK shell_config_write");
}

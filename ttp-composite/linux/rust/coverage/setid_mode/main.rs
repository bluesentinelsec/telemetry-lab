fn main() {
    if !coverage_suite::begin("setid_mode") {
        return;
    }
    use std::os::unix::fs::PermissionsExt;
    coverage_suite::write_file("/tmp/lab/mode");
    std::fs::set_permissions("/tmp/lab/mode", std::fs::Permissions::from_mode(0o4600)).unwrap();
    assert_ne!(
        std::fs::metadata("/tmp/lab/mode")
            .unwrap()
            .permissions()
            .mode()
            & 0o4000,
        0
    );
    println!("CASE_OK setid_mode");
}

pub mod files;
pub mod netio;
pub mod registry;

pub const ROOT: &str = r"C:\lab\windows-coverage";
pub fn begin(id: &str) -> bool {
    // Build-time target/CRT markers are retained in the actual executable.
    println!(concat!(
        "RUST_TARGET ",
        env!("COMPOSITE_BUILD_TARGET"),
        "\nRUST_CRT ",
        env!("COMPOSITE_BUILD_CRT"),
        "\n"
    ));
    assert_eq!(
        std::env::var("TELEMETRY_LAB_FIXTURE").as_deref(),
        Ok("1"),
        "requires isolated lab fixture"
    );
    let args: Vec<_> = std::env::args().collect();
    assert!(
        args.len() == 1 || (args.len() == 2 && args[1] == "--control"),
        "unexpected arguments"
    );
    if args.len() == 2 {
        println!("CONTROL_OK {id}");
        false
    } else {
        true
    }
}
pub fn success(id: &str) {
    println!("BEHAVIOR_OK {id}");
}
pub fn hold() {
    std::thread::sleep(std::time::Duration::from_secs(5));
}
pub fn appdata(suffix: &str) -> std::path::PathBuf {
    let app = std::env::var_os("APPDATA").expect("APPDATA missing");
    assert!(!app.is_empty());
    std::path::PathBuf::from(app).join(suffix)
}
pub fn wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(Some(0)).collect()
}
pub fn wincheck(ok: i32) {
    assert_ne!(
        ok,
        0,
        "Windows API failed: {}",
        std::io::Error::last_os_error()
    );
}

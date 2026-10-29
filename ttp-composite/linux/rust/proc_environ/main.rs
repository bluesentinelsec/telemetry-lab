// Target rule: Read environment variable from /proc files
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
fn main() {
    if !coverage_suite::begin("proc_environ") {
        return;
    }
    let data = std::fs::read("/proc/self/environ").unwrap();
    assert!(data
        .split(|b| *b == 0)
        .any(|v| v == b"TELEMETRY_LAB_FIXTURE=1"));
    println!("CASE_OK proc_environ");
}

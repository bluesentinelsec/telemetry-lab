use std::process::Command;

/// A primitive passes when its built binary runs to completion and exits 0.
/// Exit code is the only criterion, matching the C, C++, and Go suites.
#[test]
fn empty_exits_zero() {
    let status = Command::new(env!("CARGO_BIN_EXE_empty"))
        .status()
        .expect("failed to execute empty primitive");

    assert_eq!(status.code(), Some(0), "expected exit code 0, got {status:?}");
}

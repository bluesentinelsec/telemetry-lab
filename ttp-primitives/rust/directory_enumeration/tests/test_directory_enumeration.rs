use std::process::Command;

/// A primitive passes when its built binary runs to completion and exits 0.
#[test]
fn directory_enumeration_exits_zero() {
    let status = Command::new(env!("CARGO_BIN_EXE_directory_enumeration"))
        .status()
        .expect("failed to execute directory_enumeration primitive");

    assert_eq!(status.code(), Some(0), "expected exit code 0, got {status:?}");
}

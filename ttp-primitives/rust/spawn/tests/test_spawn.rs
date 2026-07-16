use std::process::Command;

#[test]
fn spawn_exits_zero() {
    let status = Command::new(env!("CARGO_BIN_EXE_spawn"))
        .status()
        .expect("failed to execute spawn primitive");

    assert_eq!(status.code(), Some(0), "expected exit code 0, got {status:?}");
}

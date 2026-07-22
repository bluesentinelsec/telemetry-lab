use std::process::Command;

/// A primitive passes when its built binary runs to completion and exits 0.
#[test]
fn pipe_ipc_exits_zero() {
    let status = Command::new(env!("CARGO_BIN_EXE_pipe_ipc"))
        .status()
        .expect("failed to execute pipe_ipc primitive");

    assert_eq!(status.code(), Some(0), "expected exit code 0, got {status:?}");
}

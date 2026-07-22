use std::process::Command;

/// A primitive passes when its built binary runs to completion and exits 0.
#[test]
fn dns_lookup_exits_zero() {
    let status = Command::new(env!("CARGO_BIN_EXE_dns_lookup"))
        .status()
        .expect("failed to execute dns_lookup primitive");

    assert_eq!(status.code(), Some(0), "expected exit code 0, got {status:?}");
}

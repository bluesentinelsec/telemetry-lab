use std::process::Command;

#[test]
fn empty_exits_zero() {
    let output = Command::new(env!("CARGO_BIN_EXE_empty"))
        .output()
        .expect("failed to execute empty primitive");

    assert!(output.status.success(), "expected exit code 0, got {:?}", output.status);
    assert!(output.stdout.is_empty(), "expected no stdout");
    assert!(output.stderr.is_empty(), "expected no stderr");
}

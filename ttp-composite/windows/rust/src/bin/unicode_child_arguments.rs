use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE unicode_child_arguments\n");
    if !fixture::begin("unicode_child_arguments") {return;}
    let output=std::process::Command::new(r"C:\lab\windows-coverage\fixtures\helper.exe").arg("marker\u{00a0}value").output().unwrap();
    print!("{}",String::from_utf8_lossy(&output.stdout));
    assert_eq!(output.status.code(),Some(43),"Unicode helper did not confirm exact argument");
    fixture::success("unicode_child_arguments");
}

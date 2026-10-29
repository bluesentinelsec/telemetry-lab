// Target rule: Potential CommandLine Obfuscation Using Unicode Characters
// Sigma rule ID: efe8a84a-0bef-c646-b13a-5a3cbe2b01b9
// Ruleset path: sigma/sysmon/threat-hunting/process_creation/proc_creation_win_susp_cli_obfuscation_unicode.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE unicode_child_arguments\n");
    if !fixture::begin("unicode_child_arguments") {return;}
    let output=std::process::Command::new(r"C:\lab\windows-coverage\fixtures\helper.exe").arg("marker\u{00a0}value").output().unwrap();
    print!("{}",String::from_utf8_lossy(&output.stdout));
    assert_eq!(output.status.code(),Some(43),"Unicode helper did not confirm exact argument");
    fixture::success("unicode_child_arguments");
}

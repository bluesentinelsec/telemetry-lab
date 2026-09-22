use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE powershell_profile\n");
    if !fixture::begin("powershell_profile") {
        return;
    }
    fixture::files::copy_verified(
        r"C:\lab\windows-coverage\fixtures\profile.ps1",
        fixture::appdata(r"Microsoft\Windows\PowerShell\Microsoft.PowerShell_profile.ps1"),
    );

    fixture::success("powershell_profile");
}

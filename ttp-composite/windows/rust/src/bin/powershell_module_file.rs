use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE powershell_module_file");if !fixture::begin("powershell_module_file") {return;}
fixture::files::copy_verified("C:\\lab\\windows-coverage\\fixtures\\text.txt", std::path::PathBuf::from(std::env::var_os("USERPROFILE").unwrap()).join("Documents\\WindowsPowerShell\\Modules\\TelemetryLabFixture\\TelemetryLabFixture.psm1"));
fixture::success("powershell_module_file");}

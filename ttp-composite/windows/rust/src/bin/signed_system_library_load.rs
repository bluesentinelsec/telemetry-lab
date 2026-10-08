use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE signed_system_library_load\n");
    if !fixture::begin("signed_system_library_load") {return;}
    use windows_sys::Win32::{Foundation::FreeLibrary,System::LibraryLoader::*};
    unsafe {
        assert!(GetModuleHandleW(fixture::wide("RstrtMgr.dll").as_ptr()).is_null());
        let expected=r"C:\Windows\System32\RstrtMgr.dll";
        let module=LoadLibraryW(fixture::wide(expected).as_ptr());assert!(!module.is_null());
        let mut path=[0u16;260];let n=GetModuleFileNameW(module,path.as_mut_ptr(),260);
        assert!(n>0 && n<260);assert!(String::from_utf16(&path[..n as usize]).unwrap().eq_ignore_ascii_case(expected));
        fixture::wincheck(FreeLibrary(module));
    }
    fixture::success("signed_system_library_load");
}

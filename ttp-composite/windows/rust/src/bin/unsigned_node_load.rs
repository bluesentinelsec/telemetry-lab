use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE unsigned_node_load\n");
    if !fixture::begin("unsigned_node_load") {
        return;
    }
    use windows_sys::Win32::{Foundation::FreeLibrary, System::LibraryLoader::*};
    unsafe {
        let path = fixture::wide(r"C:\lab\windows-coverage\fixtures\fixture.node");
        let module = LoadLibraryW(path.as_ptr());
        assert!(!module.is_null());
        let proc =
            GetProcAddress(module, b"fixture_answer\0".as_ptr()).expect("missing fixture export");
        let answer: unsafe extern "C" fn() -> i32 = std::mem::transmute(proc);
        assert_eq!(answer(), 42);
        fixture::wincheck(FreeLibrary(module));
    }

    fixture::success("unsigned_node_load");
}

use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE creation_time_change\n");
    if !fixture::begin("creation_time_change") {
        return;
    }
    use windows_sys::Win32::{
        Foundation::*, Storage::FileSystem::*, System::Time::SystemTimeToFileTime,
    };
    unsafe {
        let path = fixture::wide(r"C:\lab\windows-coverage\work\timestamp.txt");
        let file = CreateFileW(
            path.as_ptr(),
            FILE_READ_ATTRIBUTES | FILE_WRITE_ATTRIBUTES,
            FILE_SHARE_READ,
            std::ptr::null(),
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            std::ptr::null_mut(),
        );
        assert_ne!(file, INVALID_HANDLE_VALUE);
        let mut st: SYSTEMTIME = std::mem::zeroed();
        st.wYear = 2019;
        st.wMonth = 1;
        st.wDay = 1;
        let mut desired: FILETIME = std::mem::zeroed();
        let mut observed: FILETIME = std::mem::zeroed();
        fixture::wincheck(SystemTimeToFileTime(&st, &mut desired));
        fixture::wincheck(SetFileTime(
            file,
            &desired,
            std::ptr::null(),
            std::ptr::null(),
        ));
        fixture::wincheck(GetFileTime(
            file,
            &mut observed,
            std::ptr::null_mut(),
            std::ptr::null_mut(),
        ));
        assert_eq!(
            (desired.dwLowDateTime, desired.dwHighDateTime),
            (observed.dwLowDateTime, observed.dwHighDateTime)
        );
        fixture::wincheck(CloseHandle(file));
    }

    fixture::success("creation_time_change");
}

use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE raw_owned_volume_read\n");
    if !fixture::begin("raw_owned_volume_read") {return;}
    use windows_sys::Win32::{Foundation::*,Storage::FileSystem::*};
    let device=std::env::var("TELEMETRY_LAB_RAW_DEVICE").unwrap();
    let suffix=device.strip_prefix(r"\\.\PhysicalDrive").expect("invalid owned device");
    assert!(!suffix.is_empty() && suffix.bytes().all(|c|c.is_ascii_digit()));
    unsafe {
        let path=fixture::wide(&device);
        let h=CreateFileW(path.as_ptr(),GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,std::ptr::null(),OPEN_EXISTING,0,std::ptr::null_mut());
        assert_ne!(h,INVALID_HANDLE_VALUE);
        let mut data=[0u8;512];let mut n=0;
        fixture::wincheck(ReadFile(h,data.as_mut_ptr(),512,&mut n,std::ptr::null_mut()));
        fixture::wincheck(CloseHandle(h));assert_eq!(n,512);
        for (i,b) in data.iter().enumerate(){assert_eq!(*b,(i%251) as u8);}
    }
    fixture::success("raw_owned_volume_read");
}

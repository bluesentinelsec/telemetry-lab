use crate::wide;
use windows_sys::Win32::{
    Foundation::{ERROR_FILE_NOT_FOUND, ERROR_SUCCESS},
    System::Registry::*,
};
pub fn set_verified(path: &str, name: &str, value: &str) {
    let (path, name, value) = (wide(path), wide(name), wide(value));
    unsafe {
        let mut key = std::ptr::null_mut();
        assert_eq!(
            RegOpenKeyExW(
                HKEY_CURRENT_USER,
                path.as_ptr(),
                0,
                KEY_SET_VALUE | KEY_QUERY_VALUE,
                &mut key
            ),
            ERROR_SUCCESS
        );
        let size = (value.len() * 2) as u32;
        assert_eq!(
            RegSetValueExW(key, name.as_ptr(), 0, REG_SZ, value.as_ptr().cast(), size),
            ERROR_SUCCESS
        );
        let mut actual = [0u16; 1024];
        let mut length = (actual.len() * 2) as u32;
        let mut kind = 0;
        assert_eq!(
            RegQueryValueExW(
                key,
                name.as_ptr(),
                std::ptr::null(),
                &mut kind,
                actual.as_mut_ptr().cast(),
                &mut length
            ),
            ERROR_SUCCESS
        );
        assert_eq!(kind, REG_SZ);
        assert_eq!(length, size);
        assert_eq!(&actual[..value.len()], &value);
        assert_eq!(RegCloseKey(key), ERROR_SUCCESS);
    }
}
pub fn delete_runmru() {
    let path = wide(r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU");
    unsafe {
        assert_eq!(
            RegDeleteTreeW(HKEY_CURRENT_USER, path.as_ptr()),
            ERROR_SUCCESS
        );
        let mut key = std::ptr::null_mut();
        assert_eq!(
            RegOpenKeyExW(HKEY_CURRENT_USER, path.as_ptr(), 0, KEY_READ, &mut key),
            ERROR_FILE_NOT_FOUND
        );
    }
}

pub fn set_dword(path:&str,name:&str,value:u32) {
 let(path,name)=(wide(path),wide(name));unsafe {let mut key=std::ptr::null_mut();assert_eq!(RegOpenKeyExW(HKEY_CURRENT_USER,path.as_ptr(),0,KEY_SET_VALUE|KEY_QUERY_VALUE,&mut key),ERROR_SUCCESS);
 assert_eq!(RegSetValueExW(key,name.as_ptr(),0,REG_DWORD,(&value as *const u32).cast(),4),ERROR_SUCCESS);
 let(mut actual,mut size,mut kind)=(0u32,4u32,0u32);assert_eq!(RegQueryValueExW(key,name.as_ptr(),std::ptr::null(),&mut kind,(&mut actual as *mut u32).cast(),&mut size),ERROR_SUCCESS);
 assert_eq!((actual,size,kind),(value,4,REG_DWORD));assert_eq!(RegCloseKey(key),ERROR_SUCCESS);}
}

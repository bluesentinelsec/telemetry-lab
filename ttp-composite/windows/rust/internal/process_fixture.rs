use crate::{wide,wincheck};
use std::{os::windows::process::CommandExt,process::{Child,Command},time::Duration};
use windows_sys::Win32::{Foundation::*,System::{Threading::*,Diagnostics::ToolHelp::*,LibraryLoader::*}};
struct ChildGuard(Child);
impl Drop for ChildGuard {fn drop(&mut self){let _=self.0.kill();let _=self.0.wait();}}
struct Handle(HANDLE);
impl Drop for Handle {fn drop(&mut self){unsafe{CloseHandle(self.0);}}}
pub fn run(remote:bool) {
 let child=ChildGuard(Command::new(r"C:\Windows\System32\ping.exe").args(["-n","10","-w","1000","127.0.0.1"]).creation_flags(CREATE_NO_WINDOW).spawn().unwrap());
 std::thread::sleep(Duration::from_millis(200));let pid=child.0.id();
 unsafe {
 let target=Handle(OpenProcess(PROCESS_ALL_ACCESS,0,pid));assert!(!target.0.is_null());assert_eq!(GetProcessId(target.0),pid);
 if !remote{return;}
 let local=GetProcAddress(GetModuleHandleW(wide("kernel32.dll").as_ptr()),c"GetCurrentProcessId".as_ptr().cast()).unwrap() as usize;
 let mut owner=std::ptr::null_mut();wincheck(GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,local as *const u16,&mut owner));
 let mut filename=[0u16;260];let n=GetModuleFileNameW(owner,filename.as_mut_ptr(),260);assert!(n>0 && n<260);
 let fullname=String::from_utf16(&filename[..n as usize]).unwrap();let name=fullname.rsplit('\\').next().unwrap();
 let snap=Handle(CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,pid));assert_ne!(snap.0,INVALID_HANDLE_VALUE);
 let mut me:MODULEENTRY32W=std::mem::zeroed();me.dwSize=std::mem::size_of_val(&me) as u32;let mut more=Module32FirstW(snap.0,&mut me);let mut base=0usize;
 while more!=0 {let end=me.szModule.iter().position(|&x|x==0).unwrap();if String::from_utf16(&me.szModule[..end]).unwrap().eq_ignore_ascii_case(name){base=me.modBaseAddr as usize;break;}more=Module32NextW(snap.0,&mut me);}
 assert_ne!(base,0);let address=base+local-owner as usize;
 let start:unsafe extern "system" fn(*mut std::ffi::c_void)->u32=std::mem::transmute(address);
 let thread=Handle(CreateRemoteThread(target.0,std::ptr::null(),0,Some(start),std::ptr::null(),0,std::ptr::null_mut()));assert!(!thread.0.is_null());
 assert_eq!(WaitForSingleObject(thread.0,5000),WAIT_OBJECT_0);let mut code=0;wincheck(GetExitCodeThread(thread.0,&mut code));assert_eq!(code,pid);
 }
}

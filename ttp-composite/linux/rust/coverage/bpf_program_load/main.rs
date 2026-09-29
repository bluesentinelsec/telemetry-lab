use coverage_suite as fixture;
fn main() {if !fixture::begin("bpf_program_load") {return;}
let insns:[u8;16]=[0xb7,0,0,0,0,0,0,0,0x95,0,0,0,0,0,0,0];let license=b"GPL\0";let mut attr=[0u64;18];attr[0]=1|(2<<32);attr[1]=insns.as_ptr() as u64;attr[2]=license.as_ptr() as u64;unsafe {let fd=libc::syscall(libc::SYS_bpf,5,attr.as_ptr(),std::mem::size_of_val(&attr)) as i32;assert!(fd>=0,"{}",std::io::Error::last_os_error());assert_eq!(libc::close(fd),0);}
println!("CASE_OK bpf_program_load");
}

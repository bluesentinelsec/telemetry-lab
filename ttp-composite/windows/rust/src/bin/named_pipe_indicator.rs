use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE named_pipe_indicator\n");
    if !fixture::begin("named_pipe_indicator") {
        return;
    }
    use windows_sys::Win32::{Foundation::*, Storage::FileSystem::*, System::Pipes::*};
    unsafe {
        let path = fixture::wide(r"\\.\pipe\testPipe");
        let server = CreateNamedPipeW(
            path.as_ptr(),
            PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE,
            PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT,
            1,
            1024,
            1024,
            5000,
            std::ptr::null(),
        );
        assert_ne!(server, INVALID_HANDLE_VALUE);
        let client = CreateFileW(
            path.as_ptr(),
            GENERIC_READ | GENERIC_WRITE,
            0,
            std::ptr::null(),
            OPEN_EXISTING,
            0,
            std::ptr::null_mut(),
        );
        assert_ne!(client, INVALID_HANDLE_VALUE);
        assert!(
            ConnectNamedPipe(server, std::ptr::null_mut()) != 0
                || GetLastError() == ERROR_PIPE_CONNECTED
        );
        let message = b"telemetry-lab\0";
        let mut response = [0u8; 14];
        let mut n = 0;
        fixture::wincheck(WriteFile(
            client,
            message.as_ptr(),
            message.len() as u32,
            &mut n,
            std::ptr::null_mut(),
        ));
        assert_eq!(n as usize, message.len());
        fixture::wincheck(ReadFile(
            server,
            response.as_mut_ptr(),
            response.len() as u32,
            &mut n,
            std::ptr::null_mut(),
        ));
        assert_eq!(n as usize, message.len());
        assert_eq!(&response, message);
        fixture::wincheck(WriteFile(
            server,
            response.as_ptr(),
            response.len() as u32,
            &mut n,
            std::ptr::null_mut(),
        ));
        assert_eq!(n as usize, message.len());
        fixture::wincheck(ReadFile(
            client,
            response.as_mut_ptr(),
            response.len() as u32,
            &mut n,
            std::ptr::null_mut(),
        ));
        assert_eq!(n as usize, message.len());
        assert_eq!(&response, message);
        fixture::wincheck(CloseHandle(client));
        fixture::wincheck(DisconnectNamedPipe(server));
        fixture::wincheck(CloseHandle(server));
    }

    fixture::success("named_pipe_indicator");
}

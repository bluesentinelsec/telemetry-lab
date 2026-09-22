#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE named_pipe_indicator" << "\n";
    if (!fixture_begin(argc,argv,"named_pipe_indicator")) return 0;
    const char *path="\\\\.\\pipe\\testPipe";
    HANDLE server=CreateNamedPipeA(path,PIPE_ACCESS_DUPLEX|FILE_FLAG_FIRST_PIPE_INSTANCE,PIPE_TYPE_BYTE|PIPE_READMODE_BYTE|PIPE_WAIT,1,1024,1024,5000,NULL);
    CHECK(server!=INVALID_HANDLE_VALUE);
    HANDLE client=CreateFileA(path,GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); CHECK(client!=INVALID_HANDLE_VALUE);
    CHECK(ConnectNamedPipe(server,NULL) || GetLastError()==ERROR_PIPE_CONNECTED);
    const char message[]="telemetry-lab"; char response[sizeof message]; DWORD n;
    CHECK(WriteFile(client,message,sizeof message,&n,NULL) && n==sizeof message);
    CHECK(ReadFile(server,response,sizeof response,&n,NULL) && n==sizeof message && !memcmp(message,response,n));
    CHECK(WriteFile(server,response,n,&n,NULL) && n==sizeof message);
    CHECK(ReadFile(client,response,sizeof response,&n,NULL) && n==sizeof message && !memcmp(message,response,n));
    CHECK(CloseHandle(client)); CHECK(DisconnectNamedPipe(server)); CHECK(CloseHandle(server));
    success("named_pipe_indicator");
    return 0;
}

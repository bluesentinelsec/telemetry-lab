#include "../common.hpp"
#include <wchar.h>

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE raw_owned_volume_read" << "\n";
    if (!fixture_begin(argc,argv,"raw_owned_volume_read")) return 0;
    const char *device=getenv("TELEMETRY_LAB_RAW_DEVICE");
    CHECK(device && !strncmp(device,"\\\\.\\PhysicalDrive",17) && strlen(device)>17);
    for(const char *p=device+17;*p;p++) CHECK(*p>='0' && *p<='9');
    HANDLE h=CreateFileA(device,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL); CHECK(h!=INVALID_HANDLE_VALUE);
    unsigned char data[512]; DWORD n=0; CHECK(ReadFile(h,data,sizeof data,&n,NULL)); CHECK(n==sizeof data);
    CHECK(CloseHandle(h)); for(size_t i=0;i<sizeof data;i++) CHECK(data[i]==(unsigned char)(i%251));
    success("raw_owned_volume_read");
    return 0;
}

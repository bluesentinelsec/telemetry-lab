#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"tcp_connect_public_path")) return 0;
    char image[MAX_PATH]; DWORD n=GetModuleFileNameA(NULL,image,sizeof image);
    CHECK(n>0 && n<sizeof image && !_stricmp(image,"C:\\Users\\Public\\telemetry-lab\\probe.exe"));
    tcp_exchange(49152);
    success("tcp_connect_public_path");
    return 0;
}

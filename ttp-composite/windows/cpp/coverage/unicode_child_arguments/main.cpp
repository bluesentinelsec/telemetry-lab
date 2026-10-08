#include "../common.hpp"
#include <wchar.h>

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE unicode_child_arguments" << "\n";
    if (!fixture_begin(argc,argv,"unicode_child_arguments")) return 0;
    STARTUPINFOW si; PROCESS_INFORMATION pi;
    memset(&si,0,sizeof si); memset(&pi,0,sizeof pi); si.cb=sizeof si;
    wchar_t command[]=L"C:\\lab\\windows-coverage\\fixtures\\helper.exe marker\u00a0value";
    CHECK(CreateProcessW(L"C:\\lab\\windows-coverage\\fixtures\\helper.exe",command,NULL,NULL,FALSE,0,NULL,NULL,&si,&pi));
    CHECK(WaitForSingleObject(pi.hProcess,10000)==WAIT_OBJECT_0);
    DWORD code=0; CHECK(GetExitCodeProcess(pi.hProcess,&code)); CHECK(code==43);
    CHECK(CloseHandle(pi.hThread)); CHECK(CloseHandle(pi.hProcess));
    success("unicode_child_arguments");
    return 0;
}

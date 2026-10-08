#include "../common.hpp"
#include <wchar.h>

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE signed_system_library_load" << "\n";
    if (!fixture_begin(argc,argv,"signed_system_library_load")) return 0;
    CHECK(GetModuleHandleW(L"RstrtMgr.dll")==NULL);
    HMODULE module=LoadLibraryW(L"C:\\Windows\\System32\\RstrtMgr.dll"); CHECK(module!=NULL);
    wchar_t path[MAX_PATH]; DWORD n=GetModuleFileNameW(module,path,MAX_PATH); CHECK(n>0 && n<MAX_PATH);
    CHECK(!_wcsicmp(path,L"C:\\Windows\\System32\\RstrtMgr.dll")); CHECK(FreeLibrary(module));
    success("signed_system_library_load");
    return 0;
}

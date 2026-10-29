// Target rule: Prefetch File Deleted
// Sigma rule ID: 1e50ff2d-08cc-b108-b8c8-3327cf39794f
// Ruleset path: sigma/sysmon/file/file_delete/file_delete_win_delete_prefetch.yml
#include "../internal/common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE delete_prefetch_fixture");
    if(!fixture_begin(argc,argv,"delete_prefetch_fixture")) return 0;
    CHECK(remove("C:\\Windows\\Prefetch\\TELEMETRYLABFIXTURE.pf")==0); DWORD attr=GetFileAttributesA("C:\\Windows\\Prefetch\\TELEMETRYLABFIXTURE.pf"); CHECK(attr==INVALID_FILE_ATTRIBUTES && GetLastError()==ERROR_FILE_NOT_FOUND);
    success("delete_prefetch_fixture"); return 0;
}

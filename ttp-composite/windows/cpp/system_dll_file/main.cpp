// Target rule: Files With System DLL Name In Unsuspected Locations
// Sigma rule ID: 47b821bf-c853-813b-eaa2-be2620f42a1d
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_system_dll_files.yml
#include "../internal/common.hpp"
#include "../internal/expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE system_dll_file" << "\n";
    if(!fixture_begin(argc,argv,"system_dll_file")) return 0;
    copy_verified(ROOT "\\fixtures\\fixture.node","C:\\lab\\windows-coverage\\work\\secur32.dll");
    success("system_dll_file"); return 0;
}

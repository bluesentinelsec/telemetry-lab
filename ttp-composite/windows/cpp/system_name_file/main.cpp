// Target rule: Files With System Process Name In Unsuspected Locations
// Sigma rule ID: eccfe194-f618-b054-3986-7f7529f079f1
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_system_file.yml
#include "../internal/common.hpp"
#include "../internal/expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE system_name_file" << "\n";
    if(!fixture_begin(argc,argv,"system_name_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\svchost.exe");
    success("system_name_file"); return 0;
}

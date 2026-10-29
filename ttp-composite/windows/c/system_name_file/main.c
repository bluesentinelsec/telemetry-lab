// Target rule: Files With System Process Name In Unsuspected Locations
// Sigma rule ID: eccfe194-f618-b054-3986-7f7529f079f1
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_system_file.yml
#include "../internal/common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE system_name_file");
    if(!fixture_begin(argc,argv,"system_name_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\svchost.exe");
    success("system_name_file"); return 0;
}

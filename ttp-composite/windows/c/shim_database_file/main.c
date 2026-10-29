// Target rule: New Custom Shim Database Created
// Sigma rule ID: 4211e288-60d6-2bb1-01c3-b7b3191126a9
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_new_shim_database.yml
#include "../internal/common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE shim_database_file");
    if(!fixture_begin(argc,argv,"shim_database_file")) return 0;
    copy_verified(ROOT "\\fixtures\\text.txt","C:\\Windows\\AppPatch\\Custom\\telemetry-lab-fixture.sdb");
    success("shim_database_file"); return 0;
}

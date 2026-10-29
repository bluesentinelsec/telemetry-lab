// Target rule: Uncommon Process Access Rights For Target Image
// Sigma rule ID: 0d9cc92d-3ed8-beeb-dea9-8447f14fc31e
// Ruleset path: sigma/sysmon/process_access/proc_access_win_susp_all_access_uncommon_target.yml
#include "../internal/common.h"
#include "../process_fixture.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE process_access_ping");
    if(!fixture_begin(argc,argv,"process_access_ping")) return 0;
    process_fixture(0);
    success("process_access_ping"); return 0;
}

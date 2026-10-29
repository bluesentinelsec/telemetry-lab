// Target rule: Remote Thread Creation In Uncommon Target Image
// Sigma rule ID: 43e75355-271c-2069-4eca-cc2e117f8510
// Ruleset path: sigma/sysmon/create_remote_thread/create_remote_thread_win_susp_uncommon_target_image.yml
#include "../internal/common.h"
#include "../internal/process_fixture.h"
#include "../internal/expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE remote_thread_ping");
    if(!fixture_begin(argc,argv,"remote_thread_ping")) return 0;
    process_fixture(1);
    success("remote_thread_ping"); return 0;
}

// Target rule: Suspicious File Created In PerfLogs
// Sigma rule ID: 8822f47b-fcbf-b189-f9a1-10961c8f7cd0
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_perflogs_susp_files.yml
#include "../internal/common.h"
#include "../internal/expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE perflogs_file");
    if(!fixture_begin(argc,argv,"perflogs_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\PerfLogs\\telemetry-lab\\fixture.exe");
    success("perflogs_file"); return 0;
}

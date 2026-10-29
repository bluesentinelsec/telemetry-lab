// Target rule: Suspicious Screensaver Binary File Creation
// Sigma rule ID: b7a6c875-41bf-5648-744f-d236cceb1c26
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_creation_scr_binary_file.yml
#include "../internal/common.h"
#include "../internal/expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE screensaver_file");
    if(!fixture_begin(argc,argv,"screensaver_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\fixture.scr");
    success("screensaver_file"); return 0;
}

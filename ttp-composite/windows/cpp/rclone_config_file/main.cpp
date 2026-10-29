// Target rule: Rclone Config File Creation
// Sigma rule ID: 1446e210-e8da-42a9-e7bf-8fb30a60366b
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_rclone_config_files.yml
#include "../internal/common.hpp"
#include "../internal/expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE rclone_config_file" << "\n";
    if(!fixture_begin(argc,argv,"rclone_config_file")) return 0;
    copy_verified(ROOT "\\fixtures\\text.txt","C:\\Users\\Public\\.config\\rclone\\telemetry-lab-fixture.conf");
    success("rclone_config_file"); return 0;
}

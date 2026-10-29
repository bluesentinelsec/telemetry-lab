// Target rule: Suspicious Binaries and Scripts in Public Folder
// Sigma rule ID: ef4c38c9-e26f-dcfe-1cbe-6323bafb8f39
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_public_folder_extension.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE public_binary");
    if (!fixture_begin(argc,argv,"public_binary")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\Users\\Public\\telemetry-lab\\fixture.exe");
    success("public_binary");
    return 0;
}

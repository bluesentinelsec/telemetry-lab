// Target rule: Suspicious Double Extension Files
// Sigma rule ID: c69c8c8d-4188-72ea-ca61-a2a1a80612b3
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_double_extension.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE double_extension_file");
    if (!fixture_begin(argc,argv,"double_extension_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\report.pdf.exe");
    success("double_extension_file");
    return 0;
}

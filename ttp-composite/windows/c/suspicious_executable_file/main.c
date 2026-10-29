// Target rule: Suspicious Executable File Creation
// Sigma rule ID: 9512176f-0e9f-7f30-fa82-d414c1c80248
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_executable_creation.yml
#include "../internal/common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE suspicious_executable_file");
    if (!fixture_begin(argc,argv,"suspicious_executable_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\lab.sys.exe");
    success("suspicious_executable_file");
    return 0;
}

// Target rule: Potential Persistence Via Microsoft Office Startup Folder
// Sigma rule ID: be512a1b-170e-acff-f35d-0e4b44caa2a3
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_office_startup_persistence.yml
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE office_startup_file" << "\n";
    if (!fixture_begin(argc,argv,"office_startup_file")) return 0;
    char path[MAX_PATH]; appdata_path(path,sizeof path,"Microsoft\\Word\\STARTUP\\telemetry-lab-fixture.rtf");
    copy_verified(ROOT "\\fixtures\\document.rtf",path);
    success("office_startup_file");
    return 0;
}

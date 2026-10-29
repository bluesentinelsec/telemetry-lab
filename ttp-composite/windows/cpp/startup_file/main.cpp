// Target rule: Startup Folder File Write
// Sigma rule ID: daaf04a9-5b60-e331-6611-a3a32797e550
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_startup_folder_file_write.yml
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE startup_file" << "\n";
    if (!fixture_begin(argc,argv,"startup_file")) return 0;
    char path[MAX_PATH]; appdata_path(path,sizeof path,"Microsoft\\Windows\\Start Menu\\Programs\\Startup\\telemetry-lab-fixture.txt");
    copy_verified(ROOT "\\fixtures\\text.txt",path);
    success("startup_file");
    return 0;
}

// Target rule: Suspicious LNK Double Extension File Created
// Sigma rule ID: 6b7cbf57-a67c-6e5a-61c6-4d92d02fff3e
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_lnk_double_extension.yml
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE double_extension_lnk" << "\n";
    if (!fixture_begin(argc,argv,"double_extension_lnk")) return 0;
    copy_verified(ROOT "\\fixtures\\fixture.lnk","C:\\lab\\windows-coverage\\work\\report.pdf.lnk");
    success("double_extension_lnk");
    return 0;
}

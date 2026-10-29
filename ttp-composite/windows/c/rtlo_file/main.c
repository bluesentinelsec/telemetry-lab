// Target rule: Potential File Extension Spoofing Using Right-to-Left Override
// Sigma rule ID: 1522de8d-352b-1bb8-509b-932d2dd4bb60
// Ruleset path: sigma/sysmon/file/file_event/file_event_win_susp_right_to_left_override_extension_spoofing.yml
#include "../internal/common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE rtlo_file");
    if(!fixture_begin(argc,argv,"rtlo_file")) return 0;
    copy_verified_w(L"C:\\lab\\windows-coverage\\fixtures\\helper.exe",L"C:\\lab\\windows-coverage\\work\\report\u202efdp.exe");
    success("rtlo_file"); return 0;
}

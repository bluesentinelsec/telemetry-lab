#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE powershell_profile" << "\n";
    if (!fixture_begin(argc,argv,"powershell_profile")) return 0;
    char path[MAX_PATH]; appdata_path(path,sizeof path,"Microsoft\\Windows\\PowerShell\\Microsoft.PowerShell_profile.ps1");
    copy_verified(ROOT "\\fixtures\\profile.ps1",path);
    success("powershell_profile");
    return 0;
}

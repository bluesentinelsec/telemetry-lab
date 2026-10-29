// Target rule: RunMRU Registry Key Deletion - Registry
// Sigma rule ID: ec2a6d71-1139-d6f1-c39e-e9fc35500540
// Ruleset path: sigma/sysmon/registry/registry_delete/registry_delete_runmru.yml
#include "../internal/common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE registry_runmru_delete" << "\n";
    if (!fixture_begin(argc,argv,"registry_runmru_delete")) return 0;
    const char *path="Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU";
    CHECK(RegDeleteTreeA(HKEY_CURRENT_USER,path)==ERROR_SUCCESS);
    HKEY key=NULL; CHECK(RegOpenKeyExA(HKEY_CURRENT_USER,path,0,KEY_READ,&key)==ERROR_FILE_NOT_FOUND);
    success("registry_runmru_delete");
    return 0;
}

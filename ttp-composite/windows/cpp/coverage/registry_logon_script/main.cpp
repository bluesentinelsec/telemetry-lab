#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_logon_script" << "\n";
    if(!fixture_begin(argc,argv,"registry_logon_script")) return 0;
    set_registry_verified("Environment", "UserInitMprLogonScript", "C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_logon_script"); return 0;
}

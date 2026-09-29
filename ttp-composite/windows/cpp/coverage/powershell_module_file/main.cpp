#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE powershell_module_file\n";
    if(!fixture_begin(argc,argv,"powershell_module_file")) return 0;
    char path[MAX_PATH]; const char *profile=getenv("USERPROFILE");CHECK(profile && *profile);
    int n=snprintf(path,sizeof path,"%s\\%s",profile,"Documents\\WindowsPowerShell\\Modules\\TelemetryLabFixture\\TelemetryLabFixture.psm1"); CHECK(n>0 && (size_t)n<sizeof path);
    copy_verified(ROOT "\\fixtures\\text.txt",path);
    success("powershell_module_file"); return 0;
}

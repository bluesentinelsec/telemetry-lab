#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE registry_app_paths" << "\n";
    if (!fixture_begin(argc,argv,"registry_app_paths")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\telemetry-lab-fixture.exe","","C:\\Users\\Public\\telemetry-lab\\helper.exe");
    success("registry_app_paths");
    return 0;
}

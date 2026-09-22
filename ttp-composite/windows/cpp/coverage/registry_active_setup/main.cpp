#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE registry_active_setup" << "\n";
    if (!fixture_begin(argc,argv,"registry_active_setup")) return 0;
    set_registry_verified("Software\\Microsoft\\Active Setup\\Installed Components\\{9B9C8026-806D-41E2-992A-909553D7A52A}","StubPath","C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_active_setup");
    return 0;
}

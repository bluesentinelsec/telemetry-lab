#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE registry_screensaver" << "\n";
    if (!fixture_begin(argc,argv,"registry_screensaver")) return 0;
    set_registry_verified("Control Panel\\Desktop","SCRNSAVE.EXE","C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_screensaver");
    return 0;
}

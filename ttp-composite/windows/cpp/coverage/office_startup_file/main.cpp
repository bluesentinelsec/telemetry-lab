#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE office_startup_file" << "\n";
    if (!fixture_begin(argc,argv,"office_startup_file")) return 0;
    char path[MAX_PATH]; appdata_path(path,sizeof path,"Microsoft\\Word\\STARTUP\\telemetry-lab-fixture.rtf");
    copy_verified(ROOT "\\fixtures\\document.rtf",path);
    success("office_startup_file");
    return 0;
}

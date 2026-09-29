#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE rclone_config_file" << "\n";
    if(!fixture_begin(argc,argv,"rclone_config_file")) return 0;
    copy_verified(ROOT "\\fixtures\\text.txt","C:\\Users\\Public\\.config\\rclone\\telemetry-lab-fixture.conf");
    success("rclone_config_file"); return 0;
}

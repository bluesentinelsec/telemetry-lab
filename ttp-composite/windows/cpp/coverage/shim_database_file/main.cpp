#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE shim_database_file" << "\n";
    if(!fixture_begin(argc,argv,"shim_database_file")) return 0;
    copy_verified(ROOT "\\fixtures\\text.txt","C:\\Windows\\AppPatch\\Custom\\telemetry-lab-fixture.sdb");
    success("shim_database_file"); return 0;
}

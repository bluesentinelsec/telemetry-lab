#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE shim_database_file");
    if(!fixture_begin(argc,argv,"shim_database_file")) return 0;
    copy_verified(ROOT "\\fixtures\\text.txt","C:\\Windows\\AppPatch\\Custom\\telemetry-lab-fixture.sdb");
    success("shim_database_file"); return 0;
}

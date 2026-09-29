#include "../common.hpp"
#include "../process_fixture.h"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE process_access_ping\n";
    if(!fixture_begin(argc,argv,"process_access_ping")) return 0;
    process_fixture(0);
    success("process_access_ping"); return 0;
}

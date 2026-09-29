#include "../common.hpp"
#include "../process_fixture.h"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE remote_thread_ping\n";
    if(!fixture_begin(argc,argv,"remote_thread_ping")) return 0;
    process_fixture(1);
    success("remote_thread_ping"); return 0;
}

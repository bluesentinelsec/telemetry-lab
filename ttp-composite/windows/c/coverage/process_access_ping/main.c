#include "../common.h"
#include "../process_fixture.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE process_access_ping");
    if(!fixture_begin(argc,argv,"process_access_ping")) return 0;
    process_fixture(0);
    success("process_access_ping"); return 0;
}

#include "../common.h"
#include "../process_fixture.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE remote_thread_ping");
    if(!fixture_begin(argc,argv,"remote_thread_ping")) return 0;
    process_fixture(1);
    success("remote_thread_ping"); return 0;
}

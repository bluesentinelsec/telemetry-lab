#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE tcp_connect_2525");
    if (!fixture_begin(argc,argv,"tcp_connect_2525")) return 0;
    tcp_exchange(2525);
    success("tcp_connect_2525");
    return 0;
}

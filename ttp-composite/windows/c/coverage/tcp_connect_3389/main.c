#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE tcp_connect_3389");
    if (!fixture_begin(argc,argv,"tcp_connect_3389")) return 0;
    tcp_exchange(3389);
    success("tcp_connect_3389");
    return 0;
}

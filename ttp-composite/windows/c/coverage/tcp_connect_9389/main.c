#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE tcp_connect_9389");
    if (!fixture_begin(argc,argv,"tcp_connect_9389")) return 0;
    tcp_exchange(9389);
    success("tcp_connect_9389");
    return 0;
}

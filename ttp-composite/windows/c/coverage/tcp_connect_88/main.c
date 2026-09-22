#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE tcp_connect_88");
    if (!fixture_begin(argc,argv,"tcp_connect_88")) return 0;
    tcp_exchange(88);
    success("tcp_connect_88");
    return 0;
}

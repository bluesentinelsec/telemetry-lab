#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"tcp_connect_88")) return 0;
    tcp_exchange(88);
    success("tcp_connect_88");
    return 0;
}

#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE tcp_connect_2525");
    if (!fixture_begin(argc,argv,"tcp_connect_2525")) { Sleep(5000); return 0; }
    tcp_exchange(2525);
    Sleep(5000); /* Same post-I/O lifetime in every TCP case and control. */
    success("tcp_connect_2525");
    return 0;
}

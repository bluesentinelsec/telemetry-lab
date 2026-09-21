#include "../network.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"reverse_shell")) return 0;
    tcp_exchange("127.0.0.1",1);
    printf("CASE_OK reverse_shell\n");
    return 0;
}

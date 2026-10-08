#include "../common.hpp"
#include "../utility.h"
int main(int argc,char **argv) {if (!fixture_begin(argc,argv,"nodeport_exchange")) return 0;
port_exchange(30080);
std::cout << "CASE_OK nodeport_exchange\n";
}

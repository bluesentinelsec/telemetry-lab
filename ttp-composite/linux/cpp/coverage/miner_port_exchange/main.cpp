#include "../common.hpp"
#include "../utility.h"
int main(int argc,char **argv) {if (!fixture_begin(argc,argv,"miner_port_exchange")) return 0;
port_exchange(3333);
std::cout << "CASE_OK miner_port_exchange\n";
}

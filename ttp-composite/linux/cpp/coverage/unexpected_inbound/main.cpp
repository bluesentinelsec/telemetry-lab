#include "../common.hpp"
#include "../utility.h"
int main(int argc,char **argv) {if (!fixture_begin(argc,argv,"unexpected_inbound")) return 0;
port_exchange(4447);
std::cout << "CASE_OK unexpected_inbound\n";
}

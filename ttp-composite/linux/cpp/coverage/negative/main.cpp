#include "../common.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"negative")) return 0;
    
    std::cout << "CASE_OK negative\n";
    return 0;
}

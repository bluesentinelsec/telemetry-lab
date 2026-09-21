#include "../process.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"memfd_execute")) return 0;
    execute_helper(NULL,1);
    std::cout << "CASE_OK memfd_execute\n";
    return 0;
}

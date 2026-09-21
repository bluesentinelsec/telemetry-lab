#include "../process.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"exec_shm")) return 0;
    execute_helper("/dev/shm/lab-helper",0);
    std::cout << "CASE_OK exec_shm\n";
    return 0;
}

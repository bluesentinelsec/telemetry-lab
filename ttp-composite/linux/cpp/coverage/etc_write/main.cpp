#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"etc_write")) return 0;
    file_write("/etc/lab_fixture");
    std::cout << "CASE_OK etc_write\n";
    return 0;
}

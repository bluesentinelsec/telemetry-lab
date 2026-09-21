#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"monitored_write")) return 0;
    file_write("/boot/lab_fixture");
    std::cout << "CASE_OK monitored_write\n";
    return 0;
}

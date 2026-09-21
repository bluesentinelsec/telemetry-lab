#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"repository_write")) return 0;
    file_write("/etc/apt/sources.list.d/lab.list");
    std::cout << "CASE_OK repository_write\n";
    return 0;
}

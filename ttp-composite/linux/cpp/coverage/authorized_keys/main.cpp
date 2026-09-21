#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"authorized_keys")) return 0;
    file_write("/root/.ssh/authorized_keys");
    std::cout << "CASE_OK authorized_keys\n";
    return 0;
}

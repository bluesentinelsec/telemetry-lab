#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"ssh_read")) return 0;
    file_read("/root/.ssh/lab_key");
    std::cout << "CASE_OK ssh_read\n";
    return 0;
}

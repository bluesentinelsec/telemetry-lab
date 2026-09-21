#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"sensitive_read")) return 0;
    file_read("/etc/shadow");
    std::cout << "CASE_OK sensitive_read\n";
    return 0;
}

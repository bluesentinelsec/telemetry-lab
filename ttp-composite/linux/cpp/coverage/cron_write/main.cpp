#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"cron_write")) return 0;
    file_write("/etc/cron.d/lab_fixture");
    std::cout << "CASE_OK cron_write\n";
    return 0;
}

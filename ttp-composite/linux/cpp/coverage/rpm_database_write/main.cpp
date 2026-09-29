#include "../file_io.hpp"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"rpm_database_write")) return 0;
    file_write("/var/lib/rpm/telemetry-lab-fixture");
    std::cout << "CASE_OK rpm_database_write\n";
    return 0;
}

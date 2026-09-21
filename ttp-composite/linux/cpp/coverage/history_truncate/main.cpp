#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"history_truncate")) return 0;
    truncate_file("/root/.bash_history");
    std::cout << "CASE_OK history_truncate\n";
    return 0;
}

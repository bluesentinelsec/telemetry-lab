#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"binary_rename")) return 0;
    fs::rename("/usr/bin/lab_old", "/usr/bin/lab_new");
    CHECK(!fs::exists("/usr/bin/lab_old")); file_read("/usr/bin/lab_new");
    std::cout << "CASE_OK binary_rename\n";
    return 0;
}

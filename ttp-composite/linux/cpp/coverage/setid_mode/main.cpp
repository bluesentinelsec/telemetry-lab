#include "../file_io.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"setid_mode")) return 0;
    file_write("/tmp/lab/mode");
    fs::permissions("/tmp/lab/mode", fs::perms::owner_read | fs::perms::owner_write | fs::perms::set_uid);
    CHECK((fs::status("/tmp/lab/mode").permissions() & fs::perms::set_uid) != fs::perms::none);
    std::cout << "CASE_OK setid_mode\n";
    return 0;
}

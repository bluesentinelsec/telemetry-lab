#include "../common.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"sensitive_symlink")) return 0;
    fs::create_symlink("/etc/shadow", "/tmp/lab/link");
    CHECK(fs::read_symlink("/tmp/lab/link") == "/etc/shadow");
    CHECK(fs::remove("/tmp/lab/link"));
    std::cout << "CASE_OK sensitive_symlink\n";
    return 0;
}

#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE public_binary" << "\n";
    if (!fixture_begin(argc,argv,"public_binary")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\Users\\Public\\telemetry-lab\\fixture.exe");
    success("public_binary");
    return 0;
}

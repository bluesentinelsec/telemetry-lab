#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE ads_executable" << "\n";
    if (!fixture_begin(argc,argv,"ads_executable")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\lab\\windows-coverage\\work\\carrier.txt:fixture.exe");
    success("ads_executable");
    return 0;
}

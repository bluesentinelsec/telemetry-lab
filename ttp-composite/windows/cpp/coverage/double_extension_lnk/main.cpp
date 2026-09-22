#include "../common.hpp"

int main(int argc, char **argv) {
    std::cout << "COMPOSITE_CASE double_extension_lnk" << "\n";
    if (!fixture_begin(argc,argv,"double_extension_lnk")) return 0;
    copy_verified(ROOT "\\fixtures\\fixture.lnk","C:\\lab\\windows-coverage\\work\\report.pdf.lnk");
    success("double_extension_lnk");
    return 0;
}

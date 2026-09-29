#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE perflogs_file\n";
    if(!fixture_begin(argc,argv,"perflogs_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\PerfLogs\\telemetry-lab\\fixture.exe");
    success("perflogs_file"); return 0;
}

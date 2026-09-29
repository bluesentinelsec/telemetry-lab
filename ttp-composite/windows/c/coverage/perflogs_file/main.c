#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE perflogs_file");
    if(!fixture_begin(argc,argv,"perflogs_file")) return 0;
    copy_verified(ROOT "\\fixtures\\helper.exe","C:\\PerfLogs\\telemetry-lab\\fixture.exe");
    success("perflogs_file"); return 0;
}

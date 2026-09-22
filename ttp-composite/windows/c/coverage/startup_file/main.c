#include "../common.h"

int main(int argc, char **argv) {
    puts("COMPOSITE_CASE startup_file");
    if (!fixture_begin(argc,argv,"startup_file")) return 0;
    char path[MAX_PATH]; appdata_path(path,sizeof path,"Microsoft\\Windows\\Start Menu\\Programs\\Startup\\telemetry-lab-fixture.txt");
    copy_verified(ROOT "\\fixtures\\text.txt",path);
    success("startup_file");
    return 0;
}

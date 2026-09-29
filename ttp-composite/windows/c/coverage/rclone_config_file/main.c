#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE rclone_config_file");
    if(!fixture_begin(argc,argv,"rclone_config_file")) return 0;
    char path[MAX_PATH]; const char *profile=getenv("USERPROFILE");CHECK(profile && *profile);
    int n=snprintf(path,sizeof path,"%s\\%s",profile,".config\\rclone\\telemetry-lab-fixture.conf"); CHECK(n>0 && (size_t)n<sizeof path);
    copy_verified(ROOT "\\fixtures\\text.txt",path);
    success("rclone_config_file"); return 0;
}

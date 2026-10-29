// Target rule: Create Symlink Over Sensitive Files
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"sensitive_symlink")) return 0;
    CHECK(symlink("/etc/shadow","/tmp/lab/link") == 0);
    char buf[64]={0}; CHECK(readlink("/tmp/lab/link",buf,sizeof(buf)-1) == 11);
    CHECK(!strcmp(buf,"/etc/shadow")); CHECK(unlink("/tmp/lab/link") == 0);
    printf("CASE_OK sensitive_symlink\n");
    return 0;
}

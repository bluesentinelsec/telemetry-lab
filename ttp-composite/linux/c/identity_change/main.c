// Target rule: Non sudo setuid
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"
#include "../internal/utility.h"
int main(int argc,char **argv) {if (!fixture_begin(argc,argv,"identity_change")) return 0;
CHECK(getuid()==0); CHECK(setuid(2000)==0); CHECK(getuid()==2000 && geteuid()==2000);
printf("CASE_OK identity_change\n");
}

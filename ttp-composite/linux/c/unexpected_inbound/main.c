// Target rule: Unexpected inbound connection source
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"
#include "../internal/utility.h"
int main(int argc,char **argv) {if (!fixture_begin(argc,argv,"unexpected_inbound")) return 0;
port_exchange(4447);
printf("CASE_OK unexpected_inbound\n");
}

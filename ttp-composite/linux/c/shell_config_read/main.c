// Target rule: Read Shell Configuration File
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"
#include "../internal/utility.h"
int main(int argc,char **argv) {
if (!fixture_begin(argc,argv,"shell_config_read")) return 0;
verify_bytes("/root/.bashrc", fixture_payload, sizeof(fixture_payload)-1);
printf("CASE_OK shell_config_read\n");
}

// Target rule: Decoding Payload in Container
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../internal/common.h"
#include "../launch_fixture.h"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"decode_base64")) return 0;
    const char *args[] = {"/usr/bin/base64", "--decode", "/tmp/lab/encoded", NULL};
    launch_checked(args, "telemetry-lab-fixture\n", NULL, NULL);
    printf("CASE_OK decode_base64\n");
    return 0;
}

// Target rule: PTRACE attached to process
// Ruleset: Falco; exact rule name is the identifier in harness/manifest.json.
#include "../process.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"ptrace_attach")) return 0;
    trace_child();
    printf("CASE_OK ptrace_attach\n");
    return 0;
}

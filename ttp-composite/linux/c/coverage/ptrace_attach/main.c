#include "../process.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"ptrace_attach")) return 0;
    trace_child();
    printf("CASE_OK ptrace_attach\n");
    return 0;
}

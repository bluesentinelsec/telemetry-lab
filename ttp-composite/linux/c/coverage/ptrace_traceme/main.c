#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"ptrace_traceme")) return 0;
    pid_t pid=fork(); CHECK(pid >= 0);
    if (!pid) { CHECK(ptrace(PTRACE_TRACEME,0,NULL,NULL) == 0); _exit(0); }
    child_ok(pid);
    printf("CASE_OK ptrace_traceme\n");
    return 0;
}

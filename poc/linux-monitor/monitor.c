// PoC user-space loader: spawn-and-trace.
//
// Forks the target and stops it *before* it execs, arms the BPF filter on the
// target's tgid, then releases it. This guarantees telemetry is captured from
// the very first instruction (including the exec itself), and that the scope is
// exactly the target process tree -- descendants are added by the BPF fork hook.

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <sys/wait.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "monitor.skel.h"

enum evt_type { EVT_SYSCALL = 0, EVT_FORK, EVT_EXEC, EVT_EXIT };

struct event {
    unsigned int pid, tid, aux;
    unsigned long long syscall;
    unsigned char type;
    char comm[16];
};

static volatile int target_exited = 0;
static int target_tgid = 0;

static int handle_event(void *ctx, void *data, size_t sz)
{
    const struct event *e = data;
    switch (e->type) {
    case EVT_SYSCALL:
        printf("SYS   pid=%-6u tid=%-6u comm=%-16s nr=%llu\n", e->pid, e->tid, e->comm, e->syscall);
        break;
    case EVT_FORK:
        printf("FORK  pid=%-6u -> child=%-6u comm=%s\n", e->pid, e->aux, e->comm);
        break;
    case EVT_EXEC:
        printf("EXEC  pid=%-6u comm=%s\n", e->pid, e->comm);
        break;
    case EVT_EXIT:
        printf("EXIT  pid=%-6u comm=%s\n", e->pid, e->comm);
        if ((int)e->pid == target_tgid)
            target_exited = 1;
        break;
    }
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: %s <command> [args...]\n", argv[0]);
        return 1;
    }

    // Fork the target and stop it before exec.
    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        return 1;
    }
    if (child == 0) {
        raise(SIGSTOP);
        execvp(argv[1], &argv[1]);
        perror("execvp");
        _exit(127);
    }

    int status;
    waitpid(child, &status, WUNTRACED); // wait for the child's SIGSTOP

    struct monitor_bpf *skel = monitor_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "failed to open/load BPF skeleton\n");
        kill(child, SIGKILL);
        return 1;
    }
    if (monitor_bpf__attach(skel)) {
        fprintf(stderr, "failed to attach BPF programs\n");
        kill(child, SIGKILL);
        monitor_bpf__destroy(skel);
        return 1;
    }

    // Seed the traced set with the target's tgid (== child pid for a new process).
    target_tgid = child;
    unsigned int key = child;
    unsigned char one = 1;
    bpf_map__update_elem(skel->maps.traced, &key, sizeof(key), &one, sizeof(one), BPF_ANY);

    struct ring_buffer *rb = ring_buffer__new(bpf_map__fd(skel->maps.events), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "failed to create ring buffer\n");
        kill(child, SIGKILL);
        monitor_bpf__destroy(skel);
        return 1;
    }

    fprintf(stderr, "[monitor] tracing target tgid=%d: %s\n", target_tgid, argv[1]);

    // Release the target -> it execs and runs, fully instrumented.
    kill(child, SIGCONT);

    while (!target_exited)
        ring_buffer__poll(rb, 100);
    ring_buffer__poll(rb, 100); // final drain
    waitpid(child, &status, 0);

    ring_buffer__free(rb);
    monitor_bpf__destroy(skel);
    return 0;
}

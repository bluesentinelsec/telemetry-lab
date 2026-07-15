// PoC BPF program: process-scoped telemetry collection.
//
// Scope = a dynamically tracked set of "traced" thread-group ids (processes).
// User space seeds the set with the target's tgid before it execs; this program
// then (a) records every syscall made by any traced process, and (b) grows the
// set to include descendants by watching fork. Everything outside the set is
// ignored, so only the target process tree is observed.

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>

char LICENSE[] SEC("license") = "GPL";

#define MAX_TRACED 8192

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_TRACED);
    __type(key, __u32);   // tgid
    __type(value, __u8);
} traced SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1 << 24);
} events SEC(".maps");

enum evt_type { EVT_SYSCALL = 0, EVT_FORK, EVT_EXEC, EVT_EXIT };

struct event {
    __u32 pid;      // tgid
    __u32 tid;      // thread id
    __u32 aux;      // fork: child tgid
    __u64 syscall;  // syscall number
    __u8  type;
    char  comm[16];
};

static __always_inline int is_traced(__u32 tgid)
{
    return bpf_map_lookup_elem(&traced, &tgid) != 0;
}

SEC("tp/raw_syscalls/sys_enter")
int on_sys_enter(struct trace_event_raw_sys_enter *ctx)
{
    __u64 pt = bpf_get_current_pid_tgid();
    __u32 tgid = pt >> 32, tid = (__u32)pt;
    if (!is_traced(tgid))
        return 0;
    struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e)
        return 0;
    e->type = EVT_SYSCALL;
    e->pid = tgid;
    e->tid = tid;
    e->aux = 0;
    e->syscall = ctx->id;
    bpf_get_current_comm(e->comm, sizeof(e->comm));
    bpf_ringbuf_submit(e, 0);
    return 0;
}

SEC("tp/sched/sched_process_fork")
int on_fork(struct trace_event_raw_sched_process_fork *ctx)
{
    __u32 ppid = ctx->parent_pid, cpid = ctx->child_pid;
    if (!is_traced(ppid))
        return 0;
    __u8 one = 1;
    bpf_map_update_elem(&traced, &cpid, &one, BPF_ANY);
    struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e)
        return 0;
    e->type = EVT_FORK;
    e->pid = ppid;
    e->tid = ppid;
    e->aux = cpid;
    e->syscall = 0;
    bpf_get_current_comm(e->comm, sizeof(e->comm)); // current task is the parent
    bpf_ringbuf_submit(e, 0);
    return 0;
}

SEC("tp/sched/sched_process_exec")
int on_exec(struct trace_event_raw_sched_process_exec *ctx)
{
    __u64 pt = bpf_get_current_pid_tgid();
    __u32 tgid = pt >> 32;
    if (!is_traced(tgid))
        return 0;
    struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e)
        return 0;
    e->type = EVT_EXEC;
    e->pid = tgid;
    e->tid = (__u32)pt;
    e->aux = 0;
    e->syscall = 0;
    bpf_get_current_comm(e->comm, sizeof(e->comm));
    bpf_ringbuf_submit(e, 0);
    return 0;
}

SEC("tp/sched/sched_process_exit")
int on_exit(struct trace_event_raw_sched_process_template *ctx)
{
    __u64 pt = bpf_get_current_pid_tgid();
    __u32 tgid = pt >> 32, tid = (__u32)pt;
    if (!is_traced(tgid))
        return 0;
    // Only the group leader's exit means the process is gone.
    if (tgid != tid)
        return 0;
    struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (e) {
        e->type = EVT_EXIT;
        e->pid = tgid;
        e->tid = tid;
        e->aux = 0;
        e->syscall = 0;
        bpf_get_current_comm(e->comm, sizeof(e->comm));
        bpf_ringbuf_submit(e, 0);
    }
    bpf_map_delete_elem(&traced, &tgid);
    return 0;
}

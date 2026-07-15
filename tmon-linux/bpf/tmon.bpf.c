// SPDX-License-Identifier: GPL-2.0
//
// tmon kernel-side capture. CO-RE / libbpf. Attaches to a handful of stable
// tracepoints and emits one tmon_event per observed action, but only for tasks
// whose thread-group id is in the `traced` map. User space seeds that map with
// the target's tgid (while the target is stopped, before exec) and this program
// grows it to cover the whole descendant tree via the fork tracepoint.
//
// Scoping this way — rather than post-filtering in user space — means the kernel
// never even copies events for unrelated processes into the ring buffer.

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#include "tmon_event.h"

char LICENSE[] SEC("license") = "GPL";

// User space sets this before load. When false, fork records are still emitted
// but children are not added to the traced set (honors --no-follow). Marked
// const volatile so it lands in .rodata and the verifier can fold it.
const volatile _Bool follow_children = 1;

// tgid -> 1 for every process we are following. Sized for a large process tree.
struct {
	__uint(type, BPF_MAP_TYPE_HASH);
	__uint(max_entries, 8192);
	__type(key, __u32);
	__type(value, __u8);
} traced SEC(".maps");

// Kernel -> user event stream.
struct {
	__uint(type, BPF_MAP_TYPE_RINGBUF);
	__uint(max_entries, 1 << 24); // 16 MiB
} events SEC(".maps");

static __always_inline int is_traced(__u32 tgid)
{
	return bpf_map_lookup_elem(&traced, &tgid) != NULL;
}

// raw_syscalls:sys_enter — fires for every syscall entry on the machine. We keep
// only those from traced tasks. This is the primary telemetry signal.
SEC("tp/raw_syscalls/sys_enter")
int tmon_sys_enter(struct trace_event_raw_sys_enter *ctx)
{
	__u64 id = bpf_get_current_pid_tgid();
	__u32 tgid = id >> 32;
	if (!is_traced(tgid))
		return 0;

	struct tmon_event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
	if (!e)
		return 0;

	e->ts_ns = bpf_ktime_get_ns();
	e->kind = TMON_SYSCALL;
	e->pid = tgid;
	e->tid = (__u32)id;
	e->child_pid = 0;
	e->syscall_nr = ctx->id;
	e->exit_code = 0;
	e->_pad = 0;

	// ctx->args is a long[6]; copy the scalar register values verbatim. These
	// must be constant-offset reads off ctx — a loop makes clang compute a moving
	// ctx pointer, which the verifier rejects for tracepoint context. Pointer
	// arguments are decoded later in user space, not here.
	e->args[0] = (__u64)ctx->args[0];
	e->args[1] = (__u64)ctx->args[1];
	e->args[2] = (__u64)ctx->args[2];
	e->args[3] = (__u64)ctx->args[3];
	e->args[4] = (__u64)ctx->args[4];
	e->args[5] = (__u64)ctx->args[5];

	bpf_get_current_comm(e->comm, sizeof(e->comm));
	bpf_ringbuf_submit(e, 0);
	return 0;
}

// sched_process_fork — grow the traced set to cover new children of traced
// parents, and emit a fork record. The current task is the parent here, so its
// comm is the parent's comm.
SEC("tp/sched/sched_process_fork")
int tmon_fork(struct trace_event_raw_sched_process_fork *ctx)
{
	__u32 parent_tgid = ctx->parent_pid; // tracepoint reports tgid in *_pid
	if (!is_traced(parent_tgid))
		return 0;

	__u32 child_tgid = ctx->child_pid;
	if (follow_children) {
		__u8 one = 1;
		bpf_map_update_elem(&traced, &child_tgid, &one, BPF_ANY);
	}

	struct tmon_event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
	if (!e)
		return 0;

	e->ts_ns = bpf_ktime_get_ns();
	e->kind = TMON_FORK;
	e->pid = parent_tgid;
	e->tid = (__u32)bpf_get_current_pid_tgid();
	e->child_pid = child_tgid;
	e->syscall_nr = -1;
	e->exit_code = 0;
	e->_pad = 0;
	bpf_get_current_comm(e->comm, sizeof(e->comm));
	bpf_ringbuf_submit(e, 0);
	return 0;
}

// sched_process_exec — a traced task called execve successfully; its comm and
// mapped image just changed. Useful for correlating the syscall stream to the
// program actually running.
SEC("tp/sched/sched_process_exec")
int tmon_exec(struct trace_event_raw_sched_process_exec *ctx)
{
	__u64 id = bpf_get_current_pid_tgid();
	__u32 tgid = id >> 32;
	if (!is_traced(tgid))
		return 0;

	struct tmon_event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
	if (!e)
		return 0;

	e->ts_ns = bpf_ktime_get_ns();
	e->kind = TMON_EXEC;
	e->pid = tgid;
	e->tid = (__u32)id;
	e->child_pid = 0;
	e->syscall_nr = -1;
	e->exit_code = 0;
	e->_pad = 0;
	bpf_get_current_comm(e->comm, sizeof(e->comm));
	bpf_ringbuf_submit(e, 0);
	return 0;
}

// sched_process_exit — a traced task exited. Emit an exit record and, when it is
// the thread-group leader, drop the tgid from the traced set to reclaim space.
SEC("tp/sched/sched_process_exit")
int tmon_exit(struct trace_event_raw_sched_process_template *ctx)
{
	__u64 id = bpf_get_current_pid_tgid();
	__u32 tgid = id >> 32;
	__u32 tid = (__u32)id;
	if (!is_traced(tgid))
		return 0;

	struct task_struct *task = (struct task_struct *)bpf_get_current_task();
	int exit_code = BPF_CORE_READ(task, exit_code);

	struct tmon_event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
	if (e) {
		e->ts_ns = bpf_ktime_get_ns();
		e->kind = TMON_EXIT;
		e->pid = tgid;
		e->tid = tid;
		e->child_pid = 0;
		e->syscall_nr = -1;
		e->exit_code = (exit_code >> 8) & 0xff; // wait-style status -> code
		e->_pad = 0;
		bpf_get_current_comm(e->comm, sizeof(e->comm));
		bpf_ringbuf_submit(e, 0);
	}

	if (tgid == tid)
		bpf_map_delete_elem(&traced, &tgid);
	return 0;
}

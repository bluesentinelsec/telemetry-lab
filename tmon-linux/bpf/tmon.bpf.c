// SPDX-License-Identifier: GPL-2.0
//
// tmon kernel-side capture. CO-RE / libbpf. Attaches to stable tracepoints and
// emits one tmon_event per observed action, but only for tasks whose tgid is in
// the `traced` map. User space seeds that map with the target's tgid (while the
// target is stopped, before exec) and this program grows it to cover the whole
// descendant tree via the fork tracepoint.
//
// Each syscall is reported as a SYS_ENTER (raw args) and a SYS_EXIT (return
// value); user space pairs them. Pointer arguments (paths, sockaddrs) are
// decoded at EXIT, when the kernel has already faulted the page in during the
// call, so the read is reliable rather than best-effort. The exec path comes
// from the sched_process_exec tracepoint's own filename field.
//
// Records are built in a per-CPU scratch buffer and emitted variable-length
// (offsetof(str) + str_len), so the 256-byte path buffer only costs bytes on the
// ring when a path is actually present -- which keeps ring pressure, and thus
// dropped events, low even under heavy syscall load.

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#include "tmon_event.h"

char LICENSE[] SEC("license") = "GPL";

// --- Read-only config, set by user space before load -------------------------
const volatile _Bool follow_children = 1;
const volatile _Bool decode_args = 1;
const volatile _Bool capture_returns = 1;

// Events dropped because the ring buffer was full. Read from .bss by user space.
__u64 dropped_events = 0;

struct {
	__uint(type, BPF_MAP_TYPE_HASH);
	__uint(max_entries, 8192);
	__type(key, __u32);
	__type(value, __u8);
} traced SEC(".maps");

// Per-thread stash of pointer arguments seen at enter, decoded at exit.
struct decode_stash {
	__u64 path_ptr;
	__u64 saddr_ptr;
	int path_argno;
	int saddr_argno;
};

struct {
	__uint(type, BPF_MAP_TYPE_HASH);
	__uint(max_entries, 8192);
	__type(key, __u32);
	__type(value, struct decode_stash);
} decoding SEC(".maps");

// Per-CPU scratch for building a record before emitting it (the struct is too
// large for the BPF stack).
struct {
	__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
	__uint(max_entries, 1);
	__type(key, __u32);
	__type(value, struct tmon_event);
} scratch SEC(".maps");

// Default ring size (64 MiB); user space may resize before load via --buffer-mb.
struct {
	__uint(type, BPF_MAP_TYPE_RINGBUF);
	__uint(max_entries, 1 << 26);
} events SEC(".maps");

static __always_inline int is_traced(__u32 tgid)
{
	return bpf_map_lookup_elem(&traced, &tgid) != NULL;
}

static __always_inline struct tmon_event *scratch_get(void)
{
	__u32 zero = 0;
	return bpf_map_lookup_elem(&scratch, &zero);
}

// Emit `e` variable-length: everything up to and including the used bytes of the
// trailing path buffer. Records with no path pay nothing for it.
static __always_inline void emit(struct tmon_event *e)
{
	__u32 sl = e->str_len;
	if (sl > TMON_STR_LEN)
		sl = TMON_STR_LEN;
	__u64 sz = __builtin_offsetof(struct tmon_event, str) + sl;
	if (bpf_ringbuf_output(&events, e, sz, 0) != 0)
		__sync_fetch_and_add(&dropped_events, 1);
}

// Which raw arg holds a path pointer (x86-64 numbers), or -1. execve is excluded
// on purpose: its path comes from the exec tracepoint, and its address space is
// gone by the time its sys_exit fires.
static __always_inline int path_arg_index(long nr)
{
	switch (nr) {
	case 2:   /* open */
	case 4:   /* stat */
	case 6:   /* lstat */
	case 21:  /* access */
	case 76:  /* truncate */
	case 80:  /* chdir */
	case 82:  /* rename (oldpath) */
	case 83:  /* mkdir */
	case 84:  /* rmdir */
	case 86:  /* link (oldpath) */
	case 87:  /* unlink */
	case 88:  /* symlink (target) */
	case 89:  /* readlink */
	case 90:  /* chmod */
	case 92:  /* chown */
	case 94:  /* lchown */
	case 133: /* mknod */
	case 137: /* statfs */
	case 161: /* chroot */
	case 188: /* setxattr */
	case 189: /* lsetxattr */
	case 191: /* getxattr */
	case 192: /* lgetxattr */
	case 197: /* removexattr */
		return 0;
	case 257: /* openat */
	case 258: /* mkdirat */
	case 259: /* mknodat */
	case 260: /* fchownat */
	case 262: /* newfstatat */
	case 263: /* unlinkat */
	case 264: /* renameat (oldpath) */
	case 265: /* linkat (oldpath) */
	case 267: /* readlinkat */
	case 268: /* fchmodat */
	case 269: /* faccessat */
	case 316: /* renameat2 (oldpath) */
	case 322: /* execveat */
	case 332: /* statx */
	case 437: /* openat2 */
	case 439: /* faccessat2 */
		return 1;
	default:
		return -1;
	}
}

static __always_inline int sockaddr_arg_index(long nr)
{
	switch (nr) {
	case 42: /* connect */
	case 49: /* bind */
		return 1;
	case 44: /* sendto */
		return 4;
	default:
		return -1;
	}
}

// Fill a record's decoded fields from user pointers. Used at exit (page resident
// -> reliable) and, in --no-returns mode, at enter (best-effort).
static __always_inline void decode_into(struct tmon_event *e, __u64 path_ptr,
					int path_argno, __u64 saddr_ptr,
					int saddr_argno)
{
	if (path_ptr) {
		long n = bpf_probe_read_user_str(e->str, sizeof(e->str),
						 (const void *)path_ptr);
		if (n > 0) {
			e->str_len = (n > TMON_STR_LEN) ? TMON_STR_LEN : n;
			e->str_argno = path_argno;
		}
	}
	if (saddr_ptr) {
		if (bpf_probe_read_user(e->saddr, sizeof(e->saddr),
					(const void *)saddr_ptr) == 0) {
			e->saddr_len = sizeof(e->saddr);
			e->saddr_argno = saddr_argno;
		}
	}
}

// Zero the fixed header fields (not the large trailing buffers, which are gated
// by their _len fields).
static __always_inline void init_event(struct tmon_event *e, __u32 kind,
				       __u32 tgid, __u32 tid)
{
	e->ts_ns = bpf_ktime_get_ns();
	e->kind = kind;
	e->pid = tgid;
	e->tid = tid;
	e->child_pid = 0;
	e->syscall_nr = -1;
	e->ret = 0;
	e->exit_code = 0;
	e->str_len = 0;
	e->saddr_len = 0;
	e->str_argno = -1;
	e->saddr_argno = -1;
}

SEC("tp/raw_syscalls/sys_enter")
int tmon_sys_enter(struct trace_event_raw_sys_enter *ctx)
{
	__u64 id = bpf_get_current_pid_tgid();
	__u32 tgid = id >> 32;
	__u32 tid = (__u32)id;
	if (!is_traced(tgid))
		return 0;

	struct tmon_event *e = scratch_get();
	if (!e)
		return 0;
	init_event(e, TMON_SYS_ENTER, tgid, tid);
	e->syscall_nr = ctx->id;

	__u64 a[TMON_SYSCALL_ARGS];
	a[0] = (__u64)ctx->args[0];
	a[1] = (__u64)ctx->args[1];
	a[2] = (__u64)ctx->args[2];
	a[3] = (__u64)ctx->args[3];
	a[4] = (__u64)ctx->args[4];
	a[5] = (__u64)ctx->args[5];
	e->args[0] = a[0];
	e->args[1] = a[1];
	e->args[2] = a[2];
	e->args[3] = a[3];
	e->args[4] = a[4];
	e->args[5] = a[5];

	bpf_get_current_comm(e->comm, sizeof(e->comm));

	if (decode_args) {
		int pidx = path_arg_index(ctx->id);
		int sidx = sockaddr_arg_index(ctx->id);
		__u64 pptr = (pidx >= 0 && pidx < TMON_SYSCALL_ARGS) ? a[pidx] : 0;
		__u64 sptr = (sidx >= 0 && sidx < TMON_SYSCALL_ARGS) ? a[sidx] : 0;

		if (!capture_returns) {
			decode_into(e, pptr, pidx, sptr, sidx);
		} else if (pptr || sptr) {
			struct decode_stash s = {};
			s.path_ptr = pptr;
			s.path_argno = pidx;
			s.saddr_ptr = sptr;
			s.saddr_argno = sidx;
			bpf_map_update_elem(&decoding, &tid, &s, BPF_ANY);
		}
	}

	emit(e);
	return 0;
}

SEC("tp/raw_syscalls/sys_exit")
int tmon_sys_exit(struct trace_event_raw_sys_exit *ctx)
{
	if (!capture_returns)
		return 0;

	__u64 id = bpf_get_current_pid_tgid();
	__u32 tgid = id >> 32;
	__u32 tid = (__u32)id;
	if (!is_traced(tgid))
		return 0;

	struct tmon_event *e = scratch_get();
	if (!e) {
		bpf_map_delete_elem(&decoding, &tid);
		return 0;
	}
	init_event(e, TMON_SYS_EXIT, tgid, tid);
	e->syscall_nr = ctx->id;
	e->ret = ctx->ret;

	if (decode_args) {
		struct decode_stash *s = bpf_map_lookup_elem(&decoding, &tid);
		if (s) {
			decode_into(e, s->path_ptr, s->path_argno, s->saddr_ptr,
				    s->saddr_argno);
			bpf_map_delete_elem(&decoding, &tid);
		}
	}

	bpf_get_current_comm(e->comm, sizeof(e->comm));
	emit(e);
	return 0;
}

SEC("tp/sched/sched_process_fork")
int tmon_fork(struct trace_event_raw_sched_process_fork *ctx)
{
	__u32 parent_tgid = ctx->parent_pid;
	if (!is_traced(parent_tgid))
		return 0;

	__u32 child_tgid = ctx->child_pid;
	if (follow_children) {
		__u8 one = 1;
		bpf_map_update_elem(&traced, &child_tgid, &one, BPF_ANY);
	}

	struct tmon_event *e = scratch_get();
	if (!e)
		return 0;
	init_event(e, TMON_FORK, parent_tgid,
		   (__u32)bpf_get_current_pid_tgid());
	e->child_pid = child_tgid;
	bpf_get_current_comm(e->comm, sizeof(e->comm));
	emit(e);
	return 0;
}

SEC("tp/sched/sched_process_exec")
int tmon_exec(struct trace_event_raw_sched_process_exec *ctx)
{
	__u64 id = bpf_get_current_pid_tgid();
	__u32 tgid = id >> 32;
	if (!is_traced(tgid))
		return 0;

	struct tmon_event *e = scratch_get();
	if (!e)
		return 0;
	init_event(e, TMON_EXEC, tgid, (__u32)id);
	bpf_get_current_comm(e->comm, sizeof(e->comm));

	// The exec path comes from the tracepoint's own filename field (reliable),
	// not a userspace pointer that may be gone after the image swap.
	unsigned int off = ctx->__data_loc_filename & 0xffff;
	long n = bpf_probe_read_kernel_str(e->str, sizeof(e->str),
					   (const void *)ctx + off);
	if (n > 0)
		e->str_len = (n > TMON_STR_LEN) ? TMON_STR_LEN : n;

	emit(e);
	return 0;
}

SEC("tp/sched/sched_process_exit")
int tmon_exit(struct trace_event_raw_sched_process_template *ctx)
{
	__u64 id = bpf_get_current_pid_tgid();
	__u32 tgid = id >> 32;
	__u32 tid = (__u32)id;
	if (!is_traced(tgid))
		return 0;

	bpf_map_delete_elem(&decoding, &tid);

	struct task_struct *task = (struct task_struct *)bpf_get_current_task();
	int exit_code = BPF_CORE_READ(task, exit_code);

	struct tmon_event *e = scratch_get();
	if (e) {
		init_event(e, TMON_EXIT, tgid, tid);
		e->exit_code = (exit_code >> 8) & 0xff; // wait-style status -> code
		bpf_get_current_comm(e->comm, sizeof(e->comm));
		emit(e);
	}

	if (tgid == tid)
		bpf_map_delete_elem(&traced, &tgid);
	return 0;
}

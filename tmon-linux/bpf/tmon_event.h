/* Wire format shared verbatim between the BPF program (kernel, C) and the
 * user-space engine (C++). This is the on-the-ring-buffer layout; it is a plain
 * C POD so both sides agree on it byte-for-byte. The engine translates these
 * into the richer domain model (tmon::Event) before handing them to a sink.
 *
 * Keep this header free of anything that is not valid in both a BPF C target
 * and a hosted C++ translation unit: no libc includes, no C++ constructs.
 */
#ifndef TMON_BPF_EVENT_H
#define TMON_BPF_EVENT_H

#define TMON_COMM_LEN 16
#define TMON_SYSCALL_ARGS 6

/* Kinds of records the kernel emits. Fork/exec/exit bound the process tree we
 * follow; syscall is the primary telemetry signal. */
enum tmon_kind {
	TMON_SYSCALL = 0,
	TMON_FORK = 1,
	TMON_EXEC = 2,
	TMON_EXIT = 3,
};

struct tmon_event {
	unsigned long long ts_ns; /* boot-time nanoseconds */
	unsigned int kind;        /* enum tmon_kind */
	unsigned int pid;         /* tgid (userspace "pid") */
	unsigned int tid;         /* kernel pid (thread id) */
	unsigned int child_pid;   /* TMON_FORK: tgid of the new child */
	long long syscall_nr;     /* TMON_SYSCALL: syscall number, else -1 */
	int exit_code;            /* TMON_EXIT: process exit code */
	unsigned int _pad;
	unsigned long long args[TMON_SYSCALL_ARGS]; /* TMON_SYSCALL: raw scalar args */
	char comm[TMON_COMM_LEN];                   /* task command name */
};

#endif /* TMON_BPF_EVENT_H */
